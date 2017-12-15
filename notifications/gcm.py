import requests, json


url = 'https://gcm-http.googleapis.com/gcm/send'
AUTHKEY = 'AIzaSyD2NUwHvqbAlE-7IAqoEBu_YhV0HEjVJ_w'
headers = {'Content-Type': 'application/json', 'Authorization': 'key='+AUTHKEY}


def send_gcm(gcm_token, data):
	data = {'data': {'order': data},
		'to': gcm_token
	}
	res = requests.post(url, headers=headers, json=data)
	if res.status_code >= 400:
		raise Exception("GCMError")
