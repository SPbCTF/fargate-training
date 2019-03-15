import requests
import jwt

from actions import DOWN, MUMBLE
from useragents import get


class PokupaikaClient:
    def __init__(self, host, timeout=8):
        self.url = host
        self.timeout = timeout

        self.session = requests.session()

    def pubkey(self):
        req = self.create_request("GET", "/pubkey", None)
        return self.retry_request(req).text

    def new_users(self):
        req = self.create_request("GET", "/new-users", None)
        return self.retry_request(req).text

    def register(self, username, secret, password):
        req = self.create_request(
            "POST", "/register", {"username": username, "secret": secret, "password": password})
        return self.retry_request(req)

    def login(self, username, password):
        req = self.create_request(
            "POST", "/login", {"username": username, "password": password})
        return self.retry_request(req)

    def me(self):
        req = self.create_request("GET", "/me", None)
        return self.retry_request(req).text

    def get_zakupka(self, name):
        req = self.create_request("GET", "/zakupka", {"name": name})
        return self.retry_request(req)

    def new_zaupka(self, name, description, price, accessLevel):
        req = self.create_request(
            "POST", "/zakupka", {"name": name, "description": description, "price": price, "accessLevel": accessLevel})
        return self.retry_request(req)

    def retry_request(self, req):
        try:
            resp = self.session.request(**req)
        except requests.RequestException:
            try:
                resp = self.session.request(**req, timeout=self.timeout)
            except requests.HTTPError as e:
                raise PokupaikaClientException(
                    MUMBLE, "Wrong page response code! Can't get "+req.url.split('/')[-1], e)
            except (requests.Timeout, requests.ConnectionError) as e:
                raise PokupaikaClientException(DOWN, "Can't reach server!", e)
        return resp

    def create_request(self, method, url, body):
        if method == "GET":
            return dict(
                url="http://" + self.url + url, method=method, headers={"User-Agent": get()}, params=body)
        if method == "POST":
            return dict(
                url="http://" + self.url + url, method=method, headers={"User-Agent": get()}, data=body)


class PokupaikaClientException(Exception):
    def __init__(self, exit_code, message_public, message_private):
        self.code = exit_code
        self.public = message_public
        self.private = message_private
