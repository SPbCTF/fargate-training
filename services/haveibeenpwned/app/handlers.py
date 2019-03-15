from hashlib import sha256
from binascii import hexlify, unhexlify
from re import search
import struct

def generate_password(username, email):
    m = sha256()
    m.update(username.encode('utf-8'))
    m.update(email.encode('utf-8'))
    res = m.digest()[:10]
    return hexlify(res).decode('utf-8')

def check_field(test_string):
    print(test_string)
    res = False if search("[\"'.\\/]", test_string) else True
    return res

class hash:
    def __init__(self):
        self.string = b''
    def update(self, string):
        if type(string) is str:
            string = str.encode(string, 'utf-8')
        if not self.string:
            self.string = string
        else:
            self.string += string
    def digest(self):
        def permutation(source):
            table = [1, 3, 0, 2]
            result = []
            for t in table:
                result.append(source[t])
            return bytes(result)
        register = self.string
        for j in range(3):
            for i in range(len(self.string)):
                register += (len(self.string)-i).to_bytes((len(self.string).bit_length()+7)//8, 'little')
        register += b"\x00"*(32-len(register)%32)
        xored = b"\x00"*32
        for i in range(int(len(register)/32)):
             xored = bytes(i^j for (i,j) in zip(xored, register[32*i:(32*(i+1))]))
        modulus = 8
        for i in range(10):
            regs = [xored[i:i + modulus] for i in range(0, len(xored), modulus)]
            print(regs)
            tmp = []
            for r in regs:
                t = bytes(permutation(r))
                tmp.append(t)
            xored = b""
            for t in range(len(tmp)):
                if t==0:
                    xored += bytes(tmp[t][4:])
                else:
                    xored += bytes(tmp[t])
            xored += tmp[0][:4]

        return hexlify(xored)
