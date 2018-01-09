from math import sin, cos, sqrt, atan2, radians, degrees

R = 6373.0

def get_distance(loc1, loc2):
	return get_distance_latlon(
		(loc1.latitude, loc1.longitude),
		(loc2.latitude, loc2.longitude)
	)

def get_distance_latlon(point1, point2):
	lat1 = radians(point1[0])
	lon1 = radians(point1[1])
	lat2 = radians(point2[0])
	lon2 = radians(point2[1])

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	return R * c

def get_midpoint(x1, x2, y1, y2):
    lat1 = radians(x1)
    lon1 = radians(x2)
    lat2 = radians(y1)
    lon2 = radians(y2)


    bx = cos(lat2) * cos(lon2 - lon1)
    by = cos(lat2) * sin(lon2 - lon1)
    lat3 = atan2(sin(lat1) + sin(lat2), \
           sqrt((cos(lat1) + bx) * (cos(lat1) \
           + bx) + by**2))
    lon3 = lon1 + atan2(by, cos(lat1) + bx)

    return [round(degrees(lat3), 5), round(degrees(lon3), 5)]
