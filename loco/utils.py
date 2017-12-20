import datetime
from dateutil.parser import parse
from time_aware_polyline import encode_time_aware_polyline


def is_int(s):
    if s is None:
        return False

    try:
        int(s)
        return True
    except ValueError:
        return False

def validate_otp(otp):
    if not otp:
        return False

    otp = str(otp)
    if len(otp) != 4 or not is_int(otp):
        return False

    return True

def validate_phone(phone):
    if not phone:
        return False

    phone = str(phone)
    if len(phone) != 10 or not is_int(phone):
        return False

    return True

def get_query_date(request, default=None):
    PARAM_DATE = 'date'
    date = request.query_params.get(PARAM_DATE)

    try:
        return parse(date).date()
    except:
        pass

    return default

def get_query_start_limit(request):
    PARAM_START = 'start'
    PARAM_LIMIT = 'limit'
    start = request.query_params.get(PARAM_START, 0)
    limit = request.query_params.get(PARAM_LIMIT, 10)
    return (int(start), int(limit))

def to_polyline(locations):
    if not locations:
        return ''

    points = [
        [location.latitude, 
        location.longitude, 
        location.timestamp.isoformat()] for location in locations
    ]

    return encode_time_aware_polyline(points)