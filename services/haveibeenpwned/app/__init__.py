from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_pymongo import PyMongo
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'


mongo = MongoClient(app.config['MONGO_URI']).pwned
#mongo = PyMongo(app)

from app import routes, models

