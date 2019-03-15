from binascii import hexlify

def permutation(source):
            table = [1, 5, 3, 0, 7, 2, 4, 6]
            result = []
            for t in table:
                result.append(source[t])
            return bytes(result)

def unpermutation(source):
            table = [3, 0, 5, 2, 6, 1, 7, 4]
            result = []
            for t in table:
                result.append(source[t])
            return bytes(result)

string = b"Z8WXSZMKVH8PCSYFG22NOCFCF3B53B5="
register = string

print("__________________")
print("Source: ", string)
print("__________________")
for j in range(3):
    for i in range(len(string)):
        register += (len(string)-i).to_bytes((len(string).bit_length()+7)//8, 'little')
register += b"\x00"*(32-len(register)%32)
print(register)
xored = b"\x00"*32
for i in range(int(len(register)/32)):
    xored = bytes(i^j for (i,j) in zip(xored, register[32*i:(32*(i+1))]))
print(xored)
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
hexlify(xored)

print("__________________")
print("Hash: ", xored)
print("__________________")

for i in range(10):
    regs = [xored[i:i + modulus] for i in range(0, len(xored), modulus)]
    print(regs)
    xored = b""
    for t in range(len(regs)):
        if t==(len(regs)-1):
            xored += bytes(regs[t][:4])
        else:
            xored += bytes(regs[t])
    xored = regs[-1][4:] + xored

    tmp = [xored[i:i + modulus] for i in range(0, len(xored), modulus)]
    xored = b""
    for r in tmp:
        t = bytes(unpermutation(r))
        xored += t

#regs = [xored[i:i + modulus] for i in range(0, len(xored), modulus)]
#xored = b""
#for each in regs:
#    xored += bytes(unpermutation(each))

gamma = b""
for j in range(3):
    for i in range(32):
        gamma += (32-i).to_bytes(1, 'little')
gamma += b"\x00"*(32-(len(gamma)+len(xored))%32)
register = xored+gamma
result = b"\x00"*32

print(register)
for i in range(int(len(register)/32)):
    result = bytes(i^j for (i,j) in zip(result, register[32*i:(32*(i+1))]))


print(result)