import requests

def subscribe_location(source, destination):
	if not source:
		raise Exception("source can not be empty")

	source = str(source.id)
	destination = [str(user.id) for user in destination]

	url = "http://loco.masterpeace.in:8090/api/subscribe/"
	data = {
		'source': source,
		'destination': destination
	}

	res = requests.post(url, json=data)
	if res.status_code >= 400:
		raise Exception("Failed to subscribe for location. Source: {0} Destination: {1}".format(source, destination))

def unsubscribe_location(source, destination):
	if not source:
		raise Exception("source can not be empty")
		
	source = str(source.id)
	destination = [str(user.id) for user in destination]

	url = "http://loco.masterpeace.in:8090/api/unsubscribe/"
	data = {
		'source': source,
		'destination': destination
	}

	res = requests.post(url, json=data)
	if res.status_code != 200:
		raise Exception("Failed to unsubscribe for location. Source: {0} Destination: {1}".format(source, destination))		