import subprocess
import sys
import os
import random
import string
import time


host = sys.argv[1]

def check(cmd, name):	
	r = subprocess.call(cmd, shell=True)
	if r == 101:
		print name, "OK"
		return True
	else:
		print name, "FAIL"
		return False

def randomid():
    return "".join([random.choice(string.ascii_lowercase) for i in range(10)])


while True:
	uid = randomid()
	flag = randomid()
	r1 = check("python checker.py info", "info")
	r2 = check("python checker.py check " + host, "check")
	r3 = check("python checker.py put " + host + " " + uid + " " + flag, "put")
	r4 = check("python checker.py get " + host + " " + uid + " " + flag, "get")
	if r1 and r2 and r3 and r4:
		print "ALL GODD"
	else:
		print "WE LOST"
		break
	time.sleep(1.337)