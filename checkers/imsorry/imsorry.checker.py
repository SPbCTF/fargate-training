#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from string import  ascii_letters
from random import choice
import sys
import requests as rq
import re
from base64 import b64encode
from traceback import format_exc

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "Z"
PORT = 14567
url = "http://{}:14567"
def gen_random_string(N=5):
	return "".join(choice(ascii_letters) for i in range(N))

def gen_login():
	return gen_random_string(12)

def gen_password():
	return gen_random_string(14)

def create_headers(username, password):
	auth_string = b64encode("{}:{}".format(username, password))
	headers = {"Authorization":"Basic {}".format(auth_string)}
	return headers

def register(team_addr,username="",password=""):
	if not username and not password:
		username = gen_login()
		password = gen_password()
	try:
		res = rq.post(url.format(team_addr)+"/register", data={"username":username,
											"password":password})
	except rq.exceptions.ConnectionError:
		close(DOWN)
	if not username in res.text:
		close(MUMBLE, private="Not see message after register!")
	return username, password

def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)

def info(*args):
	close(OK, "vulns: 1")

def check(*args):
	team_addr = args[0]
	username1, password1 = register(team_addr)
	headers1 = create_headers(username1, password1)
	username2, password2 = register(team_addr)
	headers2 = create_headers(username2, password2)

	# Первый пользователь публично извиняется
	random_text_for_username2 = gen_random_string(20)
	data1 = {"nickname_receiver":username2,
		"private":"false",
		"apology_text":random_text_for_username2}
	try:
		res = rq.post(url.format(team_addr)+"/apology", headers=headers1, data=data1)
	except rq.exceptions.ConnectionError:
		close(DOWN)
	if not "Вы успешно извинились".decode('utf-8') in res.text:
		close(MUMBLE, "Not see message after send apology!")

	# Второй пользователь публично извиняется
	random_text_for_username1 = gen_random_string(20)
	data2 = {"nickname_receiver":username1,
		"private":"false",
		"apology_text":random_text_for_username1}
	try:
		res = rq.post(url.format(team_addr)+"/apology", headers=headers2, data=data2)
	except rq.exceptions.ConnectionError:
		close(DOWN)
	if not "Вы успешно извинились".decode('utf-8') in res.text:
		close(MUMBLE, "Not see message after send apology!")

	# Поиск публичного извинения
	try:
		res = rq.get(url.format(team_addr)+"/apology/find?nickname_sender={}".format(username2), headers=headers1)
	except rq.exceptions.ConnectionError:
		close(DOWN)
	if not username1 in res.text:
		close(MUMBLE, "Public apology was not added")

	# Прочитать сообщение по id из поиска
	id_apology = re.findall(r"{}&amp;id=(\w+)".format(username2), res.text)[0]
	try:
		res = rq.get(url.format(team_addr)+"/apology/read?nickname_sender={}&id={}".format(username2, id_apology), headers=headers1)
	except rq.exceptions.ConnectionError:
		close(DOWN)
	if not random_text_for_username1 in res.text:
		close(MUMBLE, "Not see public apology")
	close(OK)

def put(*args):
	team_addr, flag_id, flag = args[:3]
	username, password = register(team_addr)
	username2 = gen_login()
	password2 = gen_password()
	headers = create_headers(username, password)
	data = {"nickname_receiver":username2,
			"private":"true",
			"apology_text":flag}
	try:
		res = rq.post(url.format(team_addr)+"/apology", headers=headers, data=data)
	except requests.exceptions.ConnectionError:
		close(DOWN)
	if not "Вы успешно извинились".decode('utf-8') in res.text:
		close(MUMBLE, "Not see message after send apology!")
	data = {"nickname_receiver":username2,
			"private":"false",
			"apology_text":gen_random_string(20)}
	try:
		res = rq.post(url.format(team_addr)+"/apology", headers=headers, data=data)
	except requests.exceptions.ConnectionError:
		close(DOWN)
	if not "Вы успешно извинились".decode('utf-8') in res.text:
		close(MUMBLE, "Not see message after send apology!")
	_,_ = register(team_addr, username2, password2)
	close(OK,"{}:{}".format(username2,password2))

def get(*args):
	team_addr, lpb, flag = args[:3]
	username, password = lpb.split(":")
	headers = create_headers(username, password)
	res = rq.get(url.format(team_addr)+"/input_apologies", headers=headers)
	if flag in res.text:
		close(OK)
	else:
		close(MUMBLE)

def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))

def init(*args):
    close(OK)

COMMANDS = {
    'put': put,
    'check': check,
    'get': get,
    'info': info,
    'init': init
}

def main():
    try:
	    COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private="INTERNAL ERROR:\n{}".format(format_exc()))


if __name__ == "__main__":
    main()
    # print(check("6.6.0.2"))
    
