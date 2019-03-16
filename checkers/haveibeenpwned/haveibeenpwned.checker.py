#!/usr/bin/env python3

import random
import string
import sys
import requests
import re

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "haveibeenpwned"
PORT = 5000


def generate_rand(N=16):
    return ''.join(random.choice(string.ascii_letters) for i in range(N))

def generate_email():
    return "{}@{}.{}".format(generate_rand(8), generate_rand(5), generate_rand(2))


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
        username, email = generate_rand(), generate_email()

        r = s.get("http://{}:{}/register".format(team_addr, PORT))

        csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*)">', r.text).group(1)

        r = s.post("http://{}:{}/register".format(team_addr, PORT), {
            "username": username,
            "email": email,
            "csrf_token" : csrf_token,
            "submit" : "Register"
        })

        if not 'id="creds"' in r.text:
            close(CORRUPT, "Registration failed")

        password = re.search(r'id="creds">(.*)</b>', r.text).group(1).split(" : ")[1]

        r = s.get("http://{}:{}/login".format(team_addr, PORT))

        csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*)">', r.text).group(1)

        r = s.post("http://{}:{}/login".format(team_addr, PORT), {
            "username": username,
            "password": password,
            "csrf_token" : csrf_token,
            "submit" : "Sign In"
        })

        if not 'Private Section' in r.text:
            close(CORRUPT, "Login failed")

        csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*)">', r.text).group(1)

        account = generate_rand()

        r = s.post("http://{}:{}/private".format(team_addr, PORT), {
            "account": account,
            "password": flag,
            "csrf_token" : csrf_token,
            "submit" : "Submit"
        })

        if not flag in r.text:
            close(CORRUPT, "Can't add flag", "Status code - {}".format(r.status_code) )

        close(OK, "{}:{}:{}".format(username, email, password))

    except Exception as e:
        close(MUMBLE, "PUT Failed", str(e))



def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]

    s = requests.Session()
    try:
        username, email, flag = generate_rand(14), generate_email(), generate_rand()

        r = s.get("http://{}:{}/".format(team_addr, PORT))

        if r.status_code != 200:
            close(DOWN, 'Status code is not 200')

        r = s.get("http://{}:{}/register".format(team_addr, PORT))

        csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*)">', r.text).group(1)

        r = s.post("http://{}:{}/register".format(team_addr, PORT), {
            "username": username,
            "email": email,
            "csrf_token" : csrf_token,
            "submit" : "Register"
        })

        if not 'id="creds"' in r.text:
            close(CORRUPT, "Registration failed")

        password = re.search(r'id="creds">(.*)</b>', r.text).group(1).split(" : ")[1]

        r = s.get("http://{}:{}/login".format(team_addr, PORT))

        csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*)">', r.text).group(1)

        r = s.post("http://{}:{}/login".format(team_addr, PORT), {
            "username": username,
            "password": password,
            "csrf_token" : csrf_token,
            "submit" : "Sign In"
        })

        if not 'Private Section' in r.text:
            close(CORRUPT, "Login failed")

        csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*)">', r.text).group(1)

        account = generate_rand()

        r = s.post("http://{}:{}/private".format(team_addr, PORT), {
            "account": account,
            "password": flag,
            "csrf_token" : csrf_token,
            "submit" : "Submit"
        })


        if flag not in r.text:
            close(CORRUPT, "Can't add flag")

        r = s.get("http://{}:{}/users".format(team_addr, PORT))

        if email not in r.text or username not in r.text:
            close(CORRUPT, "No acc in Hall of Fame")


        r = s.post("http://{}:{}/index".format(team_addr, PORT), {
            "Account": account,
            "apiEndpoint": "https://api.haveibeenpwned.com/unifiedsearch/"
        })

        if "pwned" not in r.text:
            close(CORRUPT, "Can't find pwned account")

        close(OK)

    except Exception as e:
        close(MUMBLE, "", str(e))


def get(*args):
    team_addr, lpb, flag = args[:3]

    s = requests.Session()
    try:
        username, email, password = lpb.split(":")

        r = s.get("http://{}:{}/login".format(team_addr, PORT))

        csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*)">', r.text).group(1)

        r = s.post("http://{}:{}/login".format(team_addr, PORT), {
            "username": username,
            "password": password,
            "csrf_token" : csrf_token,
            "submit" : "Sign In"
        })

        if not 'Private Section' in r.text:
            close(CORRUPT, "Login failed")

        if flag not in r.text:
            close(CORRUPT, 'Flag is not in the account')

        r = s.get("http://{}:{}/users".format(team_addr, PORT))

        if email not in r.text or username not in r.text:
            close(CORRUPT, "No acc in Hall of Fame")

        close(OK, "{}:{}:{}".format(username, email, password))

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
