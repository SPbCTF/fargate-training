#!/usr/bin/env python3

import random
import string
import sys
import requests
import re

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "chukcha"
PORT = 1234
HEADERS = {"Type" : "text/html"}


def generate_rand(N=16):
    return ''.join(random.choice(string.ascii_letters) for i in range(N))


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)


def put(*args):
    team_addr, flag_id, flag = args[:3]

    try:
        r = requests.request("GET", "http://{}:{}/".format(team_addr, PORT))

        filename, filesize = generate_rand(), len(flag)

        if r.status_code != 200:
            close(CORRUPT, 'Status code is not 200')

        r = requests.request("PUT", "http://{}:{}/{}".format(team_addr, PORT, filename), data=flag, headers=HEADERS)

        r = requests.request("GET", "http://{}:{}/{}".format(team_addr, PORT, filename))

        if not flag in r.text:
            close(CORRUPT, "Can't add flag" )

        close(OK, "{}:{}".format(filename, filesize))

    except Exception as e:
        close(MUMBLE, "PUT Failed")



def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]

    try:
        r = requests.request("GET", "http://{}:{}/".format(team_addr, PORT))
        filesize = random.choice(range(18,32))
        filename, flag = generate_rand(),  generate_rand(filesize)

        if r.status_code != 200:
            close(CORRUPT, 'Status code is not 200')

        r = requests.request("PUT", "http://{}:{}/{}".format(team_addr, PORT, filename), data=flag, headers=HEADERS)
        print(r.text)

        r = requests.request("GET", "http://{}:{}/{}".format(team_addr, PORT, filename))

        if not flag in r.text:
            close(CORRUPT, "Can't add flag" )

        r = requests.request("SIZE", "http://{}:{}/{}".format(team_addr, PORT, filename))

        if int(r.text) != filesize:
            close(CORRUPT, 'Size error')

        close(OK)

    except Exception as e:
        close(MUMBLE)


def get(*args):
    team_addr, lpb, flag = args[:3]

    try:
        filename, filesize = lpb.split(":")

        r = requests.request("GET", "http://{}:{}/{}".format(team_addr, PORT, filename))

        if r.status_code != 200:
            close(CORRUPT, "No flag")

        r = requests.request("SIZE", "http://{}:{}/{}".format(team_addr, PORT, filename))

        if int(r.text) != int(filesize):
            close(CORRUPT, 'Size error')

        close(OK, "{}:{}".format(filename, filesize))

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