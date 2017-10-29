from math import sin, cos, sqrt, atan2, radians

R = 6373.0

def get_distance(loc1, loc2):
	dlon = loc2.longitude - loc1.longitude
	dlat = loc2.latitude - loc1.latitude

	a = sin(dlat / 2)**2 + cos(loc1.latitude) * cos(loc2.latitude) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))
	return R * c