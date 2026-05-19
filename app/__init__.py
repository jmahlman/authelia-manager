# External Imports
from flask import Flask, session, redirect, send_from_directory, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
import logging
import os


# Flask Setup
app = Flask(__name__)
app.config.update(
SECRET_KEY                        = os.environ.get('SECRET_KEY', 'change-me-set-SECRET_KEY-env'),
SESSION_COOKIE_NAME               = "authelia-manager_session",
SESSION_COOKIE_HTTPONLY            = True,
SESSION_COOKIE_SAMESITE           = "Lax",
STATIC_FOLDER                     = "static",
TEMPLATES_FOLDER                  = "templates",
DEBUG                             = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true',
TESTING                           = False,
SQLALCHEMY_DATABASE_URI           = os.environ.get('DATABASE_URI', "sqlite:///authelia-manager.sqlite"),
SQLALCHEMY_TRACK_MODIFICATIONS    = False
)

# Logging
log_level = logging.DEBUG if app.config['DEBUG'] else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

if app.config['SECRET_KEY'] == 'change-me-set-SECRET_KEY-env':
    logger.warning("SECRET_KEY not set! Sessions will break across restarts. Set the SECRET_KEY environment variable.")

# Session Setup
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

# Database Setup
db = SQLAlchemy(app)

# Flask Login Setup
from app.models.users import users
login_manager = LoginManager()
login_manager.login_view = 'ui.ui_login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return users.query.get(int(userid))

# Import Blueprints

# API
from app.blueprints import api
app.register_blueprint(api.api)

#UI
from app.blueprints import ui
app.register_blueprint(ui.ui)

# Auto-seed users from Authelia users_database.yml
from app.helpers.seed_users import seed_users_from_authelia
seed_users_from_authelia(app, db)
