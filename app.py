import os
from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db

app = None

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(LocalDevelopmentConfig)
    app.config['SECRET_KEY'] = os.urandom(24) # Used for session management

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    app.app_context().push()
    return app, login_manager

app, login_manager = create_app()

from application.controllers import *
from application.admin_controllers import *
from application.influencer_controllers import *
from application.sponsor_controllers import *
from application.ai_controllers import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)