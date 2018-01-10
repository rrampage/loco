from dateutil import parser
import delorean


def get_time_for_polyline(iso_time):
    '''
    Iso time string to int representation
    '''
    parsed_time = parser.parse(iso_time)
    # time is represented as time since epoch in ms
    return int(delorean.Delorean(parsed_time, timezone='UTC').epoch)


def get_time_from_polyline(int_representation):
    '''
    int representation to iso time string
    '''
    delorean_time = delorean.epoch(int_representation).shift('UTC')
    return delorean_time.datetime.isoformat()


def get_coordinate_for_polyline(coordinate):
    '''
    Location coordinate to int representation
    '''
    return int(round(coordinate * 1e5))


def get_coordinate_from_polyline(int_representation):
    '''
    int representation to location coordinate
    '''
    return round(int_representation * 1e-5, 5)


def get_gpx_for_polyline(gpx):
    '''
    Convert gpx log to int representation
    '''
    return (
        get_coordinate_for_polyline(gpx[0]),
        get_coordinate_for_polyline(gpx[1]),
        get_time_for_polyline(gpx[2]),
        get_time_for_polyline(gpx[3]),
        gpx[4]
    )


def get_gpx_from_decoded(lat_rep, lon_rep, time_stamp, time_stamp_end, location_type):
    '''
    Convert int representation to gpx log
    '''
    return [
        get_coordinate_from_polyline(lat_rep),
        get_coordinate_from_polyline(lon_rep),
        get_time_from_polyline(time_stamp),
        get_time_from_polyline(time_stamp_end),
        location_type
    ]


def extend_time_aware_polyline(polyline, gpx_logs, last_gpx_log=None):
    '''
    Extend time aware polyline with gpx_logs, given last gpx log
    of the polyline. A gpx log is [lat, lng, time]
    '''
    if last_gpx_log:
        last_lat, last_lng, last_time, last_time_end, location_type = get_gpx_for_polyline(last_gpx_log)
    else:
        last_lat = last_lng = last_time = last_time_end = 0

    if polyline is None:
        polyline = ''

    if not gpx_logs:
        return polyline

    for gpx_log in gpx_logs:
        lat, lng, time_stamp, time_stamp_end, location_type = get_gpx_for_polyline(gpx_log)
        d_lat = lat - last_lat
        d_lng = lng - last_lng
        d_time = time_stamp - last_time
        d_time_end = time_stamp_end - last_time_end

        # Can be reused for any n-dimensional polyline
        for v in [d_lat, d_lng, d_time, d_time_end, location_type]:
            v = ~(v << 1) if v < 0 else v << 1
            while v >= 0x20:
                polyline += (chr((0x20 | (v & 0x1f)) + 63))
                v >>= 5
            polyline += (chr(v + 63))

        last_lat, last_lng, last_time, last_time_end = lat, lng, time_stamp, time_stamp_end

    return polyline


def encode_time_aware_polyline(gpx_logs):
    return extend_time_aware_polyline('', gpx_logs, None)


def get_decoded_dimension_from_polyline(polyline, index):
    '''
    Helper method for decoding polylines that returns
    new polyline index and decoded int part of one dimension
    '''
    result = 1
    shift = 0

    while True:
        b = ord(polyline[index]) - 63 - 1
        index += 1
        result += b << shift
        shift += 5
        if b < 0x1f:
            break

    return index, (~result >> 1) if (result & 1) != 0 else (result >> 1)


def decode_time_aware_polyline(polyline):
    '''
    Decode time aware polyline into list of gpx logs
    A gpx log is [lat, lng, time]
    '''
    gpx_logs = []
    index = lat = lng = time_stamp = time_stamp_end = 0

    while index < len(polyline):
        index, lat_part = get_decoded_dimension_from_polyline(polyline, index)
        index, lng_part = get_decoded_dimension_from_polyline(polyline, index)
        index, time_part = get_decoded_dimension_from_polyline(polyline, index)
        index, time_part_end = get_decoded_dimension_from_polyline(polyline, index)
        index, location_type = get_decoded_dimension_from_polyline(polyline, index)
        lat += lat_part
        lng += lng_part
        time_stamp += time_part
        time_stamp_end += time_part_end
        gpx_log = get_gpx_from_decoded(lat, lng, time_stamp, time_stamp_end, location_type)
        gpx_logs.append(gpx_log)

    return gpx_logs