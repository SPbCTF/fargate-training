from string import  ascii_lowercase, digits
from random import choice
import sys
import requests as rq
import re

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "imsorry"
PORT = 14567
url = "http://{}:14567"
alph = ascii_lowercase + digits
def gen_random_string(N=4):
	return "".join(choice(alph) for i in range(N))

def gen_login():
	# yzm9-g7bt-pb23
	return "{}-{}-{}".format(gen_random_string(),gen_random_string(),gen_random_string())

def gen_password():
	# 86ai95iig90cns
	return gen_random_string(14)

def register(team_addr):
	username = gen_login()
	password = gen_password()
	res = rq.post(url.format(team_addr)+"/register", data={"username":username,
											"password":password})
	print(res.text)
	if not re.findall(r"{}".format(username), res):
		close(MUMBLE, "Not see message after register!")
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

def put(*args):
	team_addr, flag_id, flag = args[:3]
	username, password = register(team_addr)


def get(*args):
	team_addr, lpb, flag = args[:3]

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
    # main()
    register("127.0.0.1")
    # pass

# Действия чекера:
# Чекер регистрирует пользователя для извинений aka test1
# Регистируеет второго пользователя aka test2
# Из под пользователя test2 извиняется перед test1 с пометкой 'Приватное извинение'

# Проверка функциональности сервиса:
# Регистрация
# Авторизация 
# Ошибка 404
