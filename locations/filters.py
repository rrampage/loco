import utils

NOISE_TIME = 10
NOISE_DISTANCE = 0.001
NOISE_SPEED = 170
NOISE_ACCURACY = 200

def is_time_noise(test_location, last_location):
    return (test_location.timestamp - last_location.timestamp).total_seconds() < NOISE_TIME

def is_distance_noise(test_location, last_location):
    return utils.get_distance(test_location, last_location) < NOISE_DISTANCE

def is_less_accurate(test_location):
    return test_location.accuracy > NOISE_ACCURACY

def is_speed_noise(test_location, last_location):
    distance =  utils.get_distance(test_location, last_location)
    time = test_location.timestamp - last_location.timestamp
    if time.total_seconds() == 0:
        return True

    speed = (distance*60*60)/time.total_seconds()
    return speed > NOISE_SPEED

def is_noise(test_location, last_location):
    return is_time_noise(test_location, last_location) or is_distance_noise(test_location, last_location) or is_speed_noise(test_location, last_location) or is_less_accurate(test_location)

def is_pitstop(test_location, last_location):
    distance =  utils.get_distance(test_location, last_location)
    time = test_location.timestamp - last_location.timestamp
    distance = distance - (test_location.accuracy + last_location.accuracy)/1000
    # if distance > 2*NOISE_DISTANCE:
    #     return False

    if time.total_seconds() == 0:
        return True
        
    speed = (distance*60*60)/time.total_seconds()
    print ((test_location.latitude, test_location.longitude, last_location.longitude, last_location.latitude, distance, time, speed))
    return speed < 3

