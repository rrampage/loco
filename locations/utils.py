from math import sin, cos, sqrt, atan2, radians, degrees
import time_aware_polyline
from datetime import timedelta

from . import polyline

R = 6373.0

TYPE_MOVE_POINT = 0
TYPE_STOP_POINT = 1

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

def get_midpoint(locations):
    latitude = 0
    longitude = 0
    count = 0
    for location in locations:
        if location.accuracy<25:
            latitude += location.latitude
            longitude += location.longitude
            count += 1


    if count == 0:
        count = 1

    return[latitude/count, longitude/count, 9, True]

def flatten_location(location):
    if not location:
        return

    return [
        location.latitude,
        location.longitude,
        location.timestamp,
        location.timestamp,
        TYPE_MOVE_POINT,
        location.accuracy
    ]

def aggregate_stop_points(locations):
    if not locations:
        return

    latitude = 0
    longitude = 0
    accuracy = 0
    count = 0
    start_time = locations[0][2]
    end_time = locations[0][3]

    for location in locations:
        if start_time > location[2]:
            start_time = location[2]
        if end_time < location[3]:
            end_time = location[3]

        if location[5]<25:
            latitude += location[0]
            longitude += location[1]
            accuracy += location[5]
            count += 1

    if count == 0:
        count = 1

    if count < 5 or end_time-start_time < timedelta(minutes=10):
        return [latitude/count, longitude/count, start_time, start_time, TYPE_MOVE_POINT, accuracy/count]
        
    return [latitude/count, longitude/count, start_time, start_time, TYPE_STOP_POINT, accuracy/count]

def to_polyline(locations):
    if not locations:
        return ''

    points = [
        [location[0], 
        location[1], 
        location[2].isoformat()] for location in locations
    ]

    return time_aware_polyline.encode_time_aware_polyline(points)


def to_rich_polyline(locations):
    if not locations:
        return ''

    points = [
        [location[0], 
        location[1], 
        location[2].isoformat(),
        location[3].isoformat(),
        location[4]] for location in locations
    ]

    return polyline.encode_time_aware_polyline(points)