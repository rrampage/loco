import redis
from django.conf import settings

CACHE_LOCATION = 'loco.masterpeace.in'
CACHE_PORT = 6174
CACHE_DB = 0

host = CACHE_LOCATION
port = CACHE_PORT
db = CACHE_DB
pool = redis.ConnectionPool(host=host, port=port, db=db, password="lokopass")
cache = redis.Redis(connection_pool=pool)

KEY_LOCATION = "location"

def set_user_location(user_id, location_data):
	cache.hmset(user_id, {KEY_LOCATION: location_data})

def get_users_location(user_ids):
	pipe = cache.pipeline()
	for id in user_ids:
		pipe.hget(id, KEY_LOCATION)
	rows = pipe.execute()
	return rows