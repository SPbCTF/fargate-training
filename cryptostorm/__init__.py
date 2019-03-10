import os

from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
)

import cryptostorm.views

print ("Server started...")