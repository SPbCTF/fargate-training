#!/usr/bin/env python3

import random
import string
import sys
import requests
import re

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "cryptostorm"
PORT = 5000

methods = {0: "SHA-1", 1: "SHA-2", 2: "Keccak", 3: "PRNG", 4: "RSA", 5: "AES"}

def generate_rand(N=16):
    return ''.join(random.choice(string.ascii_letters) for i in range(N))

def generate_name():
    return f"{generate_rand(4)}{generate_rand(3)}{generate_rand(4)}"


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)


def put(*args):
    team_addr, flag_id, flag = args[:3]
    s = requests.Session()
    try:
        r = s.get("http://{}:{}/".format(team_addr, PORT))

        name, method = generate_name(), random.choice([0,1,2,3,4,5])
        print(f"Username:{name}")
        print(f"Algorythm: {methods[method]}")

        if r.status_code != 200:
            close(CORRUPT, 'Status code is not 200')


        r = s.post("http://{}:{}/add".format(team_addr, PORT), {
            "name": name,
            "flag": flag,
            "method" : str(method)
        })

        if r.status_code != 200:
            close(MUMBLE, "Can't add flag")

        private_key = re.findall(r'хранилища:</a></p><h4 class="lead text-muted">.*</h4>', r.text)[0][46:-5]
        print(f"private_key: {private_key}")
        flag_identifier = re.findall(r'Ваш уникальный идентификатор флага: .*</p><', r.text)[0][36:-5]
        print(f"Flag identifier: {flag_identifier}")

        r = s.post("http://{}:{}/unlock/{}".format(team_addr, PORT, flag_identifier), {
            "private": private_key
        })

        if not flag in r.text:
            close(CORRUPT, "Can't add flag" )


        close(OK, "{}:{}".format(flag_identifier, private_key))

    except Exception as e:
        print(e)
        close(MUMBLE, "PUT Failed")



def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]

    s = requests.Session()
    try:
        r = s.get("http://{}:{}/".format(team_addr, PORT))

        name, method, flag = generate_name(), random.choice([0,1,2,3,4,5]), generate_rand(32)
        print(f"Username:{name}")
        print(f"Algorythm: {methods[method]}")

        if r.status_code != 200:
            close(CORRUPT, 'Status code is not 200')


        r = s.post("http://{}:{}/add".format(team_addr, PORT), {
            "name": name,
            "flag": flag,
            "method" : str(method)
        })

        if r.status_code != 200:
            close(MUMBLE, "Can't add flag")

        private_key = re.findall(r'хранилища:</a></p><h4 class="lead text-muted">.*</h4>', r.text)[0][46:-5]
        print(f"private_key: {private_key}")
        flag_identifier = re.findall(r'Ваш уникальный идентификатор флага: .*</p><', r.text)[0][36:-5]
        print(f"Flag identifier: {flag_identifier}")

        r = s.post("http://{}:{}/unlock/{}".format(team_addr, PORT, flag_identifier), {
            "private": private_key
        })

        if not flag in r.text:
            close(CORRUPT, "Can't decrypt flag" )


        close(OK)

    except Exception as e:
        close(MUMBLE)


def get(*args):
    team_addr, lpb, flag = args[:3]

    s = requests.Session()
    try:
        flag_identifier, private_key = lpb.split(":")

        r = s.post("http://{}:{}/unlock/{}".format(team_addr, PORT, flag_identifier), {
            "private": private_key
        })

        if flag not in r.text:
            close(CORRUPT, "Can't decrypt flag")

        close(OK, "{}:{}".format(flag_identifier, private_key))

    except Exception as e:
        close(CORRUPT)


def init(*args):
    close(OK)


COMMANDS = {
    'put': put,
    'check': check,
    'get': get,
    'info': info,
    'init': init
}


if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private="INTERNAL ERROR: {}".format(ex))