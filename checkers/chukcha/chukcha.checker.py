#!/usr/bin/env python3

import random
import string
import sys
import requests
import re
import time

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
    get_success = False
    try:
        filename, filesize = generate_rand(), len(flag)

        r = requests.request("PUT", "http://{}:{}/{}".format(team_addr, PORT, filename), data=flag, headers=HEADERS)

        for j in range(5):
            if r.status_code == 200:
                break
            time.sleep(1)
            r = requests.request("PUT", "http://{}:{}/{}".format(team_addr, PORT, filename), data=flag, headers=HEADERS)

        r = requests.request("GET", "http://{}:{}/{}".format(team_addr, PORT, filename))

        if not flag in r.text:
            close(MUMBLE, "Can't add flag", "Status code {}".format(r.status_code))

        close(OK, "{}:{}".format(filename, filesize))

    except Exception as e:
        close(MUMBLE, "PUT Failed", str(e))



def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]

    try:
        try:
            r = requests.request("GET", "http://{}:{}/".format(team_addr, PORT))
        except:
            close(DOWN)

        if r.status_code != 200:
            close(CORRUPT, 'Status code is not 200')

        filesize = random.choice(range(18,32))
        filename, flag = generate_rand(),  generate_rand(filesize)

        r = requests.request("PUT", "http://{}:{}/{}".format(team_addr, PORT, filename), data=flag, headers=HEADERS)

        for j in range(5):
            if r.status_code==200:
                break
            time.sleep(1)
            r = requests.request("PUT", "http://{}:{}/{}".format(team_addr, PORT, filename), data=flag, headers=HEADERS)

        if r.status_code != 200:
            close(CORRUPT, "PUT failed, status - " + str(r.status_code), r.text)

        r = requests.request("GET", "http://{}:{}/{}".format(team_addr, PORT, filename))

        if not flag in r.text:
            close(CORRUPT, "Can't add flag")

        r = requests.request("SIZE", "http://{}:{}/{}".format(team_addr, PORT, filename))
        try:
            a = int(r.text)
            if a != filesize:
                close(CORRUPT, 'Size error')
        except:
            close(CORRUPT, "Size error")

        close(OK)

    except Exception as e:
        close(MUMBLE, "", e)


def get(*args):
    team_addr, lpb, flag = args[:3]

    try:
        filename, filesize = lpb.split(":")

        r = requests.request("GET", "http://{}:{}/{}".format(team_addr, PORT, filename))

        if r.status_code != 200:
            close(MUMBLE)

        if r.text.strip() != flag:
            close(CORRUPT, "Can't get flag", "Flag-{}, returned-{}".format(flag, r.text.strip()))

        #r = requests.request("SIZE", "http://{}:{}/{}".format(team_addr, PORT, filename))
        #try:
        #    a = int(r.text)
        #    if int(r.text) != int(filesize):
        #        close(CORRUPT, 'Size error', "Size-{}, returned-{}".format(filesize, r.text.strip()))
        #except:
        #    close(CORRUPT, "Size error")
        close(OK, "{}:{}".format(filename, filesize))

    except Exception as e:
        close(MUMBLE, "", str(e))


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
