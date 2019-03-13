from string import  ascii_lowercase, digits
from random import choice
import sys
import requests as rq
import re
from base64 import b64encode

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "imsorry"
PORT = 14567
url = "http://{}:14567"
alph = ascii_lowercase + digits
def gen_random_string(N=5):
	return "".join(choice(alph) for i in range(N))

def gen_login():
	# yzm9-g7bt-pb23
	return "{}-{}-{}".format(gen_random_string(),gen_random_string(),gen_random_string())

def gen_password():
	# 86ai95iig90cns
	return gen_random_string(14)

def create_headers(username, password):
	auth_string = b64encode("{}:{}".format(username, password).encode()).decode()
	headers = {"Authorization":"Basic {}".format(auth_string)}
	return headers

def register(team_addr, username=gen_login(), password=gen_password()):
	res = rq.post(url.format(team_addr)+"/register", data={"username":username,
											"password":password})
	if not re.findall(r"{}".format(username), res.text):
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
	# ################################
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
	res = rq.post(url.format(team_addr)+"/apology", headers=headers, data=data)
	if not re.findall(r"Вы успешно извинились", res.text):
		close(MUMBLE, "Not see message after send apology!")
	close(OK,"{}:{}".format(username2,password2))

def get(*args):
	team_addr, lpb, flag = args[:3]
	username, password = lpb.split(":")
	_,_ = register(team_addr, username, password)
	headers = create_headers(username, password)
	res = rq.get(url.format(team_addr)+"/input_apologies", headers=headers)
	if flag in res.text:
		close(OK)

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
    # ./checker.py info
    # ./checker.py check 6.6.10.2
    # ./checker.py put 6.6.10.2 qweq-qweq-qweq ABCDEF1234567890ABCDEF123456789= 1
    # ./checker.py get 6.6.10.2 qweq-qweq-qweq ABCDEF1234567890ABCDEF123456789= 1
    try:
        COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private="INTERNAL ERROR: {}".format(ex))


if __name__ == "__main__":
    main()
    # gen_flag = gen_random_string(31)+"="
    # print(gen_flag)
    # put("127.0.0.1",gen_login(),gen_flag)
    # get("127.0.0.1","vk5k1-q5atz-5jhcd:vi0yqn07viawnn","l8adaffdgt8qftmlj4d43kkfizobd7e=")
    # pass

# Действия чекера:
# Чекер регистрирует пользователя для извинений aka test1
# Регистируеет второго пользователя aka test2
# Из под пользователя test2 извиняется перед test1 с пометкой 'Приватное извинение'

# Проверка функциональности сервиса:
# Регистрация
# Авторизация 
# Ошибка 404
