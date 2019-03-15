import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'h4ve1b33npwn3d'
    MONGO_URI = os.environ.get('MONGO_URI') or "mongodb://localhost:27017/"