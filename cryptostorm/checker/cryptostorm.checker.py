#!/usr/bin/env python3

import random
import string
import re
import sys
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import requests
import hashlib
from html.parser import HTMLParser

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "cryptostorm"
PORT = 5000

methods = {0: "SHA-1", 1: "SHA-2", 2: "Keccak", 3: "PRNG", 4: "RSA", 5: "AES"}
methods_inv = {v: k for k, v in methods.items()}


# Yeah, fuck imports
class HTMLTableParser(HTMLParser):
    # https://github.com/schmijos/html-table-parser-python3/blob/master/html_table_parser/parser.py
    """ This class serves as a html table parser. It is able to parse multiple
    tables which you feed in. You can access the result per .tables field.
    """

    def __init__(
            self,
            decode_html_entities=False,
            data_separator=' ',
    ):

        HTMLParser.__init__(self)

        self._parse_html_entities = decode_html_entities
        self._data_separator = data_separator

        self._in_td = False
        self._in_th = False
        self._current_table = []
        self._current_row = []
        self._current_cell = []
        self.tables = []

    def handle_starttag(self, tag, attrs):
        """ We need to remember the opening point for the content of interest.
        The other tags (<table>, <tr>) are only handled at the closing point.
        """
        if tag == 'td':
            self._in_td = True
        if tag == 'th':
            self._in_th = True

    def handle_data(self, data):
        """ This is where we save content to a cell """
        if self._in_td or self._in_th:
            self._current_cell.append(data.strip())

    def handle_charref(self, name):
        """ Handle HTML encoded characters """

        if self._parse_html_entities:
            self.handle_data(self.unescape('&#{};'.format(name)))

    def handle_endtag(self, tag):
        """ Here we exit the tags. If the closing tag is </tr>, we know that we
        can save our currently parsed cells to the current table as a row and
        prepare for a new row. If the closing tag is </table>, we save the
        current table and prepare for a new one.
        """
        if tag == 'td':
            self._in_td = False
        elif tag == 'th':
            self._in_th = False

        if tag in ['td', 'th']:
            final_cell = self._data_separator.join(self._current_cell).strip()
            self._current_row.append(final_cell)
            self._current_cell = []
        elif tag == 'tr':
            self._current_table.append(self._current_row)
            self._current_row = []
        elif tag == 'table':
            self.tables.append(self._current_table)
            self._current_table = []


def generate_rand(N=16):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(N))


def generate_name():
    return "{}-{}-{}".format(generate_rand(4), generate_rand(4), generate_rand(4))


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

        name, method = generate_name(), random.choice(range(len(methods)))
        print("Username:{}".format(name))
        print("Algo: {}".format(methods[method]))

        if r.status_code != 200:
            close(CORRUPT, 'Status code is not 200')

        r = s.post("http://{}:{}/add".format(team_addr, PORT), {
            "name": name,
            "flag": flag,
            "method" : str(method)
        })

        if r.status_code != 200:
            close(MUMBLE, "Can't add flag")

        private_key = re.search(r'хранилища:</a></p><h4 class="lead text-muted">(.*)</h4>', r.text).group(1)
        print("private_key: {}".format(private_key))
        flag_identifier = re.search(r'Ваш уникальный идентификатор флага: (.*)</p><', r.text).group(1)
        print("Flag identifier: {}".format(flag_identifier))

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

    for method in range(len(methods)):

        try:
            r = s.get("http://{}:{}/".format(team_addr, PORT))

            name, flag = generate_name(), generate_rand(32)
            print("Username:{}".format(name))
            print("Algo: {}".format(methods[method]))

            if r.status_code != 200:
                close(CORRUPT, 'Status code is not 200')

            r = s.post("http://{}:{}/add".format(team_addr, PORT), {
                "name": name,
                "flag": flag,
                "method": str(method)
            })

            if r.status_code != 200:
                close(MUMBLE, "Can't add flag")

            private_key = re.search(r'хранилища:</a></p><h4 class="lead text-muted">(.*)</h4>', r.text).group(1)
            print("private_key: {}".format(private_key))
            flag_identifier = re.search(r'Ваш уникальный идентификатор флага: (.*)</p><', r.text).group(1)
            print("Flag identifier: {}".format(flag_identifier))

            r = s.post("http://{}:{}/unlock/{}".format(team_addr, PORT, flag_identifier), {
                "private": private_key
            })

            if not flag in r.text:
                close(CORRUPT, "Can't decrypt flag")

            check_storage(team_addr, PORT, flag_identifier, private_key, flag)

        except Exception as e:
            close(MUMBLE)

    close(OK)


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

        check_storage(team_addr, PORT, flag_identifier, private_key, flag)

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


def parse_table(html):
    p = HTMLTableParser()
    p.feed(html)
    table = p.tables[0]

    # We don't need '#' and private key in data entries, so:
    header = table.pop(0)[1:-1]

    data = dict()

    # This can be turned into list of lists for better performance if necessary

    for row in table:
        data_id = int(row.pop(0))
        data[data_id] = dict(zip(header, row))

    return data


def check_public(method, public, private, flag):
    if method == 0:
        res = sha1_check(private, public)

    elif method == 1:
        res = sha2_check(private, public)

    elif method == 2:
        res = sha3_check(private, public)

    elif method == 3:
        res = PRNG_check(private, public)

    elif method == 4:
        global N
        N = 0
        global e
        e = 0
        global c
        c = []
        exec(public, globals())
        c = list(map(int, c))
        private = int(private)
        res = RSA_decrypt(private, N, c, flag)

    elif method == 5:
        res = AES_decrypt(public, private, flag)

    else:
        res = False

    if not res:
        close(CORRUPT, 'Check of public key on flags page failed for method {}'.format(methods[method]))



def get_private_key(password):
    salt = b"feeling salty, huh?"
    kdf = PBKDF2(password, salt, 64, 3)
    key = kdf[:32]
    return key


def decrypt(enc, password):
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    private_key = get_private_key(password)
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))


def AES_decrypt(enc, password, flag):
    decrypted = bytes.decode(decrypt(enc, password))
    return decrypted == flag


def sha1_check(data, hash):
    return hashlib.sha1(data.encode()).hexdigest() == hash


def sha2_check(data, hash):
    return hashlib.sha256(data.encode()).hexdigest() == hash


def sha3_check(data, hash):
    return hashlib.sha3_256(data.encode()).hexdigest() == hash


def PRNG_check(data, key):
    return hashlib.md5(data.encode()).hexdigest() == key


def Decryption(d, n, c):
    try:
        m = [chr(pow(char, d, n)) for char in c]
    except:
        close(CORRUPT, 'Check of public key on flags page failed for method RSA')
    return ''.join(m)


def RSA_decrypt(d, n, message, flag):
    return Decryption(d, n, message) == flag


def check_storage(team_addr, PORT, id, private, flag: "Only required for AES and RSA" = ''):
    try:
        r = requests.get("http://{}:{}/flags".format(team_addr, PORT))
    except Exception as e:
        close(CORRUPT, "Request for /flags failed")

    html = r.text

    try:
        data = parse_table(html)
    except Exception as e:
        close(CORRUPT, "Parsing table on /flags page failed")

    try:
        id = int(id)
        entry = data[id]

    except:
        close(CORRUPT, "No data for id {} found".format(id))

    try:
        method = methods_inv[entry['Метод']]
    except:
        close(CORRUPT, "Unknown method for id {}".format(id))
    public = entry['Открытый ключ']

    try:
        public = str(public)
        private = str(private)
        check_public(method, public, private, flag)
    except Exception as e:
       # print (e)
        close(CORRUPT, "Public key check failed for id {id}".format(id))


if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private="INTERNAL ERROR: {}".format(ex))

