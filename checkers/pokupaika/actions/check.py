from random import randint
from traceback import format_exc

import jwt
from faker import Faker
from faker.providers import ssn

from actions import CHECKER_ERROR, MUMBLE, OK
from actions.utils import random_string, random_username
from client import PokupaikaClient, PokupaikaClientException

COUNTER_MAX = 100000
META_RANGE = slice(16, 127)


def check(team_host):
    try:
        return wrapped_check(team_host)
    except PokupaikaClientException as e:
        return {"code": e.code, "public": e.public, "private": e.private}
    except (IndexError, ValueError) as e:
        return {"code": CHECKER_ERROR, "private": "{} {}".format(e, format_exc())}


def wrapped_check(team_host):
    # 0. Init
    client = PokupaikaClient(team_host)
    fake = Faker()
    fake.add_provider(ssn)

    # 1. Get pubkey
    pubkey = client.pubkey()

    # 2. Regiter
    username = random_username()
    secret = fake.ssn()
    password = random_string()

    resp_reg = client.register(username, secret, password)
    if not "zakupki" in resp_reg.url:
        return {"code": MUMBLE, "public": "Can't register", "private": {"status": resp_reg.status_code, "headers": resp_reg.headers, "url": resp_reg.url}}

    # 3. Verify jwt
    try:
        token = client.session.cookies.get('token')
        jwt.decode(token, pubkey, algorithms=["ES256"])
    except (jwt.exceptions.InvalidSignatureError, AttributeError) as e:
        return {"code": MUMBLE, "public": "Invalid token signature!", "private": {"token": token, "pubkey": pubkey, "error": e}}

    # 4. New zakupka
    name = random_string()
    description = fake.text()
    price = randint(1, 1000)
    accessLevel = 0

    resp_new = client.new_zaupka(name, description, price, accessLevel)

    # 5. Get new zakupka

    resp_zakupka = client.get_zakupka(name)
    zakupka_new = resp_zakupka.text
    if not (name in zakupka_new or description in zakupka_new or str(price) in zakupka_new or str(accessLevel) in zakupka_new):
        return {"code": MUMBLE, "public": "Can't get zakupka", "private": {"name": name, "text": zakupka_new}}

    # 6. Check if user in new users
    new_users = client.new_users()
    if not (username in new_users):
        return {"code": MUMBLE, "public": "Can't see new user on /new-users page", "private": {"username": username, "text":  new_users}}

    return {"code": OK}
