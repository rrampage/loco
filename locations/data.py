import matplotlib.pyplot as plt

import utils
from .models import UserLocation
from .filters import is_noise


def plot_location_data(user_id):
	locations = UserLocation.objects.filter(user=user_id)
	accuracy_list = []
	distance_list = []
	time_list = []
	recv_time_list = []
	noise_list = []

	plt.figure(1)

	timestamp = locations[0].timestamp
	created = locations[0].created
	start_location = locations[0]

	for i in range(1, len(locations)):
		location = locations[i]
		last_location = locations[i-1]
		
		_is_noise = is_noise(location, last_location)
		noise_list.append(_is_noise)
		if _is_noise:
			continue


		distance = utils.get_distance(location, start_location)
		distance_list.append(distance)

		time_gap = location.timestamp - timestamp
		time_list.append(time_gap.total_seconds())

		recv_time_gap = location.created - created
		recv_time_list.append(recv_time_gap.total_seconds())

		accuracy_list.append(location.accuracy)

	plt.subplot(221)
	plt.plot(distance_list)
	plt.title("Distance")
	plt.subplot(224)
	plt.plot(time_list)
	plt.title("Time Gap")
	plt.subplot(222)
	plt.plot(recv_time_list)
	plt.title("Recieved Gap")
	plt.subplot(223)
	plt.scatter(range(1, len(locations)), noise_list)
	plt.title("Accuracy")
	plt.show()
