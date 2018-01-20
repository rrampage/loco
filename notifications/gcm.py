import requests, json
from teams.models import Checkin, TeamMembership


url = 'https://gcm-http.googleapis.com/gcm/send'
AUTHKEY = 'AIzaSyD2NUwHvqbAlE-7IAqoEBu_YhV0HEjVJ_w'
headers = {'Content-Type': 'application/json', 'Authorization': 'key='+AUTHKEY}


def send_gcm(gcm_token, message):
	data = {'data': message,
		'to': gcm_token
	}
	res = requests.post(url, headers=headers, json=data)
	if res.status_code >= 400:
		raise Exception("GCMError")

def send_checkin_gcm(checkin_id):
	checkin = Checkin.objects.get(id=checkin_id)
	author = checkin.user
	targets = checkin.team.members.filter(role=TeamMembership.ROLE_ADMIN)
	message = "{0} checked in".format(author.name.title())
	for target in targets:
		send_gcm(target.gcm_token, message)