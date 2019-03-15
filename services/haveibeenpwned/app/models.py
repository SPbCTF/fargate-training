from app import mongo
from hashlib import sha256
from binascii import hexlify, unhexlify
from app.handlers import hash

class User:
    @staticmethod
    def get_users():
        tmp = mongo.users.find({"$where": "this.submitted>0"})
        res = [(i['username'], i['email']) for i in tmp]
        return res
    @staticmethod
    def check_user(user, password):
        m = sha256()
        m.update(password.encode('utf-8'))
        pwd = hexlify(m.digest()).decode('utf-8')
        try:
            res = list(mongo.users.find({"username": user, "password": pwd}))
        except:
            return False
        return True if len(res)>0 else False
    @staticmethod
    def user_exists(user):
        try:
            res = list(mongo.users.find({"username": user}))
        except:
            return False
        return True if len(res)>0 else False
    @staticmethod
    def add_user(filled_form):
        m = sha256()
        print(filled_form)
        m.update(filled_form['password'].encode('utf-8'))
        filled_form['password'] = hexlify(m.digest()).decode('utf-8')
        print(filled_form['password'])
        filled_form['submitted'] = 0
        try:
            mongo.users.insert(filled_form)
        except:
            return False
        return True

class Breach:
    @staticmethod
    def check_account(email):
        try:
            res = list(mongo.breach.find({"$where": "function(){var result = this.email==\""+email+"\"; return result}"}))
        except:
            return []
        result = []
        for r in res:
            if 'passwords' in r.keys():
                result.extend(r['passwords'])
        passwords = list(set(result))
        encrypted_passwords = []
        for each in passwords:
            m = hash()
            m.update(each)
            encrypted_passwords.append(m.digest())
        return encrypted_passwords
    @staticmethod
    def get_breached_accounts():
        try:
            res = list(mongo.breach.find())
        except:
            return []
        r = [i['email'] for i in res]
        return r
    @staticmethod
    def add_breach(email, password, submitter=None):
        try:
            if not submitter:
                res = list(mongo.breach.find({"email": email}))
                if len(res)>0:
                    mongo.breach.insert({"email": email}, {"$push": {"password": password}})
                else:
                    mongo.breach.insert({"email": email, "passwords": [password], "public": "yes"})
            else:
                res = mongo.breach.find_one({"email": email, "submitter": submitter})
                if res:
                    if password not in res['passwords']:
                        mongo.breach.update({"email": email, "submitter": submitter}, {"$push": {"passwords": password}})
                else:
                    mongo.breach.insert({"email": email, "passwords": [password], "public": "no", "submitter": submitter})
                mongo.users.update({"username": submitter}, {"$inc": {"submitted": 1}})
        except:
            return False
        return True
    @staticmethod
    def get_submitted_breachs(submitter):
        user = mongo.users.find_one({"username": submitter})
        if 'admin' in user.keys():
            res = list(mongo.breach.find())
        else:
            res = list(mongo.breach.find({"submitter": submitter}))

        for i in res:
            print(i)
            if 'email' in i.keys():
                print("!")
            if 'passwords' in i.keys():
                print("*")
        r = [(i['email'], i['passwords']) for i in res if 'email' in i.keys() and 'passwords' in i.keys()]
        print(r)
        return r