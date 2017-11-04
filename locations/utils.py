from math import sin, cos, sqrt, atan2, radians

R = 6373.0

def get_distance(loc1, loc2):
	return get_distance_latlot(
		(loc1.latitude, loc1.longitude),
		(loc2.latitude, loc2.longitude)
	)

def get_distance_latlot(point1, point2):
	lat1 = radians(point1[0])
	lon1 = radians(point1[1])
	lat2 = radians(point2[0])
	lon2 = radians(point2[1])

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	return R * c