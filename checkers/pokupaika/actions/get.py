from client import PokupaikaClient, PokupaikaClientException
from actions import OK, CORRUPT, MUMBLE, DOWN
from time import sleep
from random import randint
from traceback import format_exc
from http.client import RemoteDisconnected
from requests.exceptions import HTTPError


def get(command_ip, flag_id, flag, vuln=None):
    try:
        if int(vuln) == 1:
            return get_from_secret(command_ip, flag_id, flag)
        else:
            return get_from_zakupka(command_ip, flag_id, flag)
    except PokupaikaClientException as e:
        return {"code": e.code, "public": e.public, "private": e.private}
    except (IndexError, ValueError) as e:
        return {"code": MUMBLE, "private": "{} {}".format(e, format_exc())}


def get_from_secret(command_ip, flag_id, flag):
    client = PokupaikaClient(command_ip)

    user, password = flag_id.split(":")

    try:
        client.login(user, password)
        me = client.me()
    except PokupaikaClientException as e:
        if isinstance(e, HTTPError):
            return {"code": MUMBLE, "public": "Can't get me"}
        raise e

    if not flag in me:
        return {"code": CORRUPT, "public": "Can't find flag in me!"}

    return {"code": OK}


def get_from_zakupka(command_ip, flag_id, flag):
    client = PokupaikaClient(command_ip)

    username, password, name = flag_id.split(":")

    try:
        client.login(username, password)
        zakupka_text = client.get_zakupka(name).text
    except PokupaikaClientException as e:
        if isinstance(e, HTTPError):
            return {"code": MUMBLE, "public": "Can't get zakupka"}
        raise e

    if not flag in zakupka_text:
        return {"code": CORRUPT, "public": "Can't find flag in zakupka!"}

    return {"code": OK}
