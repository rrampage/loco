import redis, pickle
from django.conf import settings

CACHE_LOCATION = 'loco.masterpeace.in'
CACHE_PORT = 6174
CACHE_DB = 0

host = CACHE_LOCATION
port = CACHE_PORT
db = CACHE_DB
pool = redis.ConnectionPool(host=host, port=port, db=db, password="lokopass")
cache = redis.Redis(connection_pool=pool)

KEY_LOCATION = "location_"

def set_user_location(user_id, location_data):
	if not user_id or not location_data:
		return
		
	key = KEY_LOCATION + str(user_id)
	cache.set(key, pickle.dumps(location_data))

def get_users_location(user_ids):
	if not user_ids:
		return 

	keys = [KEY_LOCATION+str(id) for id in user_ids]
	rows = cache.mget(keys)
	return [pickle.loads(row) if row else None for row in rows]