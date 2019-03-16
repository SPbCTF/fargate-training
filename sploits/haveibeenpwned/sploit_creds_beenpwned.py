from hashlib import sha256
from binascii import hexlify, unhexlify

def generate_password(username, email):
    m = sha256()
    m.update(username.encode('utf-8'))
    m.update(email.encode('utf-8'))
    res = m.digest()[:10]
    return hexlify(res).decode('utf-8')

username = "JabYqlyqaMyDqkyY"
email = "OgSUgIWa@aSllY.Ok"
password = generate_password(username, email)
print(username, ":", password)