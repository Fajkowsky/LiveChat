from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from flask.ext.socketio import SocketIO

app = Flask(__name__)
app.config.from_object('config')

db = MongoEngine(app)

login_manager = LoginManager()
login_manager.login_view = "login_page"
login_manager.init_app(app)

socketio = SocketIO(app)

import views, models