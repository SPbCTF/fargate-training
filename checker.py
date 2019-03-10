from string import  ascii_uppercase, digits
from random import choice

alph = ascii_uppercase + digits
url = "http://localhost:4567/"


def gen_flag():
	return "".join([choice(alph) for i in range(31)]) + "="


class imsorry:
	def __init__(self):
		pass

	def register_user_sender(self):
		pass

	def register_uset_reciever(self):
		pass

	def auth(self):
		pass

	def add_apology(self):
		pass


if __name__ == "__main__":
	
	flag = gen_flag()
	print(flag)