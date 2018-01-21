import requests, json
from  oauth2client.service_account import ServiceAccountCredentials

from teams.models import Checkin, TeamMembership

url = 'https://fcm.googleapis.com/v1/projects/bd-tracker/messages:send'

def _get_access_token():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      '../keys/service.json', 'https://www.googleapis.com/auth/firebase.messaging')
  access_token_info = credentials.get_access_token()
  return access_token_info.access_token


headers = {
  'Authorization': 'Bearer ' + _get_access_token(),
  'Content-Type': 'application/json; UTF-8',
}

def send_gcm(gcm_token, message):
	data= {
	  	"message":{
	    "token" : gcm_token,
	    "notification" : {
	      "body" : "",
	      "title" : message,
	      }
	   }
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