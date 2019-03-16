import hashlib
import random
import string
from Crypto.Util import number
import base64
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import keccak
import gmpy2
from flask import abort

AES_BLOCK_SIZE = 16
pad = lambda s: s + (AES_BLOCK_SIZE - len(s) % AES_BLOCK_SIZE) * chr(AES_BLOCK_SIZE - len(s) % AES_BLOCK_SIZE).encode()
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def get_private_key(password):
    salt = b"feeling salty, huh?"
    kdf = PBKDF2(password, salt, 64, 3)
    key = kdf[:32]
    return key


def encrypt(raw, password):
    private_key = get_private_key(password)
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))


def decrypt(enc, password):
    private_key = get_private_key(password)
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))


def AES_encrypt(flag):
    flag = flag.encode()
    password = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(32))
    encrypted = encrypt(flag, password).decode()
    return encrypted, password

def AES_decrypt(enc, password, private):
    decrypted = bytes.decode(decrypt(enc, password))
    return decrypted == private

def sha1_encrypt(flag:string):
    try:
        key = random.uniform(100000.,10000000.)
        key = "{0:.3}".format(key)
        data = hashlib.sha1(key.encode()).hexdigest()
    except:
        data = "411350dda09fe85b4099b6c9939f57d94dca8050"
    hash = hashlib.sha1(data.encode()).hexdigest()
    return data, hash


def sha1_check(data, hash):
    return hashlib.sha1(data.encode()).hexdigest() == hash

def generate_primes()->"For fast work":
    p = number.getPrime(12)
    q = number.getPrime(10)
    return p,q

def sha2_encrypt(id:string):
    try:
        id = float(random.randint((id+100) ** 200, (id+100) ** 210))
        data = hashlib.sha256(str("{0:.30}".format(id)).encode()).hexdigest()
    except:
        data = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
    hash = hashlib.sha256(data.encode()).hexdigest()
    return data, hash

def sha2_check(data, hash):
    return hashlib.sha256(data.encode()).hexdigest() == hash

def sha3_encrypt(flag:string):
    try:
        data = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(64))
    except:
        data = "a0e570324e6ffdbc6b9c813dec968d9bad134bc0dbb061530934f4e59c2700b9"
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(data.encode())
    hash = keccak_hash.hexdigest()
    return data, hash

def sha3_check(data, hash):
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(data.encode())
    data = keccak_hash.hexdigest()
    return data == hash

def PRNG_encrypt(id)->"Well, it's MD5, actually":
    try:
        data = str(randоm.randint(id, (id+5)*200))
        key = hashlib.md5(data.encode()).hexdigest()
    except:
        data = "flag"
        key = "327a6c4304ad5938eaf0efb6cc3e53dc"
    return data, key

def PRNG_check(data, key):
    return hashlib.md5(data.encode()).hexdigest() == key

from cryptostorm import randоm

def generate_rsa():
    while True:
        e = 3
        p = number.getPrime(12)
        q = number.getPrime(10)
        n = gmpy2.mpz(p) * gmpy2.mpz(q)
        phi_n = gmpy2.mpz(p - 1) * gmpy2.mpz(q - 1)

        if gmpy2.gcd(phi_n, e) == 1:
            return n, e, phi_n

def encrypt_rsa(e, n, m):
    c = [gmpy2.powmod(ord(char),e,n) for char in m]
    return c

def decrypt_rsa(d, n, c):
    try:
        m =  [chr(gmpy2.powmod(char, d, n)) for char in c]
    except:
        print("Failed to decrypt")
        abort(400)
    return ''.join(m)

def rsa_encrypt(flag):
    n, e, phi_n = generate_rsa()
    d = gmpy2.invert(e, phi_n)
    data = encrypt_rsa(e, n, flag)
    return n, e, d, data

def rsa_decrypt(d, n, message, flag):
    return decrypt_rsa(d, n, message) == flag

