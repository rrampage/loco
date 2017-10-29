import utils

NOISE_TIME = 10
NOISE_DISTANCE = 0.1
NOISE_SPEED = 175

def is_time_noise(test_location, last_location):
	return test_location.timestsamp - last_location.timestsamp < NOISE_TIME

def is_distance_noise(test_location, last_location):
	return utils.get_distance(test_location, last_location) < NOISE_DISTANCE

def is_speed_noise(test_location, last_location):
	distance =  utils.get_distance(test_location, last_location)
	time = test_location.timestsamp - last_location.timestsamp
	speed = (distance*60*60)/time
	return speed > NOISE_SPEED

def is_noise(test_location, last_location):
	return is_time_noise(test_location, last_location) or is_distance_noise(test_location, last_location) or is_speed_noise(test_location, last_location)