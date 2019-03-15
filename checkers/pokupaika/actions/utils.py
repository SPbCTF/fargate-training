import random
import string


def random_string(l=10, charset=string.ascii_letters + string.digits):
    return ''.join(random.choice(charset) for _ in range(l))


def random_username():
    return random_string(4, string.ascii_lowercase + string.digits) + '-' + \
        random_string(4, string.ascii_lowercase + string.digits) + '-' + \
        random_string(4, string.ascii_lowercase + string.digits)
