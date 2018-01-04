import utils

NOISE_TIME = 10
NOISE_DISTANCE = 0.05
NOISE_SPEED = 150

def is_time_noise(test_location, last_location):
	return (test_location.timestamp - last_location.timestamp).total_seconds() < NOISE_TIME

def is_distance_noise(test_location, last_location):
	return utils.get_distance(test_location, last_location) < NOISE_DISTANCE

def is_speed_noise(test_location, last_location):
	distance =  utils.get_distance(test_location, last_location)
	time = test_location.timestamp - last_location.timestamp
	speed = (distance*60*60)/time.total_seconds()
	return speed > NOISE_SPEED or speed < 10

def is_noise(test_location, last_location):
	return is_time_noise(test_location, last_location) or is_distance_noise(test_location, last_location) or is_speed_noise(test_location, last_location)