import requests
from random import randint



def generate_otp():
	otp = ''
	for i in range(4):
		otp += str(randint(0, 9))

	return otp

def send_otp(phone, otp):
	url = 'https://2factor.in/API/V1/2b298643-5a36-11e6-a8cd-00163ef91450/SMS/{0}/{1}'
	url = url.format(phone, otp)
	response = requests.get(url)
	if response.status_code != 200:
		raise Exception("OTP sending failed")