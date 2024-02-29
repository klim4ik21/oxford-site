from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session
from data.db import SQLighter
from werkzeug.security import generate_password_hash, check_password_hash
from config import db_uri
from api_v1 import v1 as apiv1

from flask_session import Session
from routers.api import api_bp
from routers.friends import friends_bp
from routers.home import home_bp
from routers.login import login_bp
from routers.posts import posts_bp
from routers.profile import profile_bp
from routers.register import reg_bp
from routers.users import users_bp
from routers.messages import messages_bp

app = Flask(__name__)

# Конфигурация приложения
app.secret_key == '111'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Регистрация Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(api_bp)
app.register_blueprint(users_bp)
app.register_blueprint(friends_bp)
app.register_blueprint(login_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(reg_bp)
app.register_blueprint(messages_bp)

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
