import redis, pickle
from datetime import timedelta
from dateutil.parser import parse
from django.conf import settings
from django.utils import timezone
from locations.models import LocationStatus, PhoneStatus
from accounts.models import User

CACHE_LOCATION = 'loco.masterpeace.in'
CACHE_PORT = 6174
CACHE_DB = 0

host = CACHE_LOCATION
port = CACHE_PORT
db = CACHE_DB
pool = redis.ConnectionPool(host=host, port=port, db=db, password="lokopass")
cache = redis.Redis(connection_pool=pool)

KEY_PING = "ping_"
KEY_LAST_LOCATION = "last_location_"
KEY_STATUS = "status_"
KEY_STATUS_SIGNIN = "signin"
KEY_STATUS_LOCATION = "location"

USER_STATUS_SIGNEDIN = "signedin" 
USER_STATUS_SIGNEDOUT = "signedout" 
USER_STATUS_LOCATIONOFF = "locationoff" 
USER_STATUS_UNREACHABLE = "unreachable" 


def _clean_ping_data(ping_data):
	result = {}
	for key in ping_data:
		if key == 'id':
			continue
		elif key=='user':
			user_id = ping_data['user'].id
			result[key] = User.objects.get(id=user_id)
		else:
			result[key] = str(ping_data[key])
	return result

def get_user_ping(user_id):
	if not user_id:
		return 

	key = KEY_PING+str(user_id)
	ping = cache.get(key)
	if ping:
		return pickle.loads(cache.get(key))

	return {}

def get_user_status(user_id):
	if not user_id:
		return 

	key = KEY_STATUS + str(user_id)
	status = cache.hgetall(key)
	last_ping = get_user_ping(user_id)
	if not status.get(KEY_STATUS_SIGNIN) == 'True' or not last_ping:
		return USER_STATUS_SIGNEDOUT
	else:
		last_ping_time = parse(last_ping.get('timestamp'))
		if timezone.now() - last_ping_time > timedelta(minutes=10):
			return USER_STATUS_UNREACHABLE

		if not status.get(KEY_STATUS_LOCATION) == 'True':
			return USER_STATUS_LOCATIONOFF

	return USER_STATUS_SIGNEDIN

def set_user_signin_status(user_id, status):
	if not user_id:
		return
		
	key = KEY_STATUS + str(user_id)
	cache.hset(key, KEY_STATUS_SIGNIN, status)

def set_user_location_status(user_id, status):
	if not user_id:
		return
		
	key = KEY_STATUS + str(user_id)
	cache.hset(key, KEY_STATUS_LOCATION, status)

def set_user_ping(user_id, ping_data):
	if not user_id or not ping_data:
		return
	
	key = KEY_PING + str(user_id)
	new_ping = _clean_ping_data(ping_data)
	cache.set(key, pickle.dumps(new_ping))

	last_ping = get_user_ping(user_id)
	if not last_ping:
		return

	last_ping_time = parse(last_ping.get('timestamp'))
	if timezone.now() - last_ping_time > timedelta(minutes=10):
		PhoneStatus.objects.create(action_type=PhoneStatus.ACTION_OFF, **last_ping)
		PhoneStatus.objects.create(action_type=PhoneStatus.ACTION_ON, **new_ping)

	if not new_ping.get('latitude') and last_ping.get('latitude'):
		set_user_location_status(user_id, True)
		LocationStatus.objects.create(action_type=LocationStatus.ACTION_OFF, **last_ping)
	elif new_ping.get('latitude') and not last_ping.get('latitude'):
		set_user_location_status(user_id, False)
		LocationStatus.objects.create(action_type=LocationStatus.ACTION_ON, **new_ping)

def set_last_known_location(user_id, location_data):
	if not user_id or not location_data:
		return
		
	key = KEY_LAST_LOCATION + str(user_id)
	cache.set(key, pickle.dumps(location_data))

def get_users_last_location(user_ids):
	if not user_ids:
		return 

	keys = [KEY_LAST_LOCATION+str(id) for id in user_ids]
	rows = cache.mget(keys)
	return [pickle.loads(row) if row else None for row in rows]