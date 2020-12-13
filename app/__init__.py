from flask import Flask
import mongoengine
from flask_login import LoginManager


mongoengine.connect()
app = Flask(__name__)
app.secret_key = "wackySecretKeyOMG"
login = LoginManager(app)


from . import models, routes