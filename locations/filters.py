import utils

NOISE_TIME = 10
NOISE_DISTANCE = 0.05
NOISE_SPEED = 150
NOISE_ACCURACY = 200

# A user is on a pitstop if
PITSTOP_TIME = 600 # ... time between 2 measurements is greater than 10 min
PITSTOP_DISTANCE = 0.2 # ... and distance between 2 measurements is less than 200 metres

def is_time_noise(test_location, last_location):
    return (test_location.timestamp - last_location.timestamp).total_seconds() < NOISE_TIME

def is_distance_noise(test_location, last_location):
    return utils.get_distance(test_location, last_location) < NOISE_DISTANCE

def is_less_accurate(test_location):
    return test_location.accuracy > NOISE_ACCURACY

def is_speed_noise(test_location, last_location):
    distance =  utils.get_distance(test_location, last_location)
    time = test_location.timestamp - last_location.timestamp
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
        
    speed = (distance*60*60)/time.total_seconds()
    print ((test_location.latitude, test_location.longitude, last_location.longitude, last_location.latitude, distance, time, speed))
    return speed < 5

