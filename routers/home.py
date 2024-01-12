from flask import Blueprint, render_template, request, redirect, url_for
from data.db import SQLighter
from flask import session
from config import db_uri
from utils import get_full_image_url
from api_v1 import v1 as apiv1
import json

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    db = SQLighter(db_uri)
    if 'username' in session:
        db.update_last_seen(session['username'])

    # Вызываем функцию get_posts() непосредственно, без HTTP-запроса
    posts_response = apiv1.get_posts()  # Здесь предполагается, что get_posts возвращает ответ Flask

    # Получаем список постов из ответа
    posts_list = posts_response.json.get('posts', []) if hasattr(posts_response, 'json') else []
    user_agent = request.headers.get('User-Agent')
    if "Mobile" in user_agent:
        return redirect(url_for('home.mobile_index'))
    else:
        return render_template('index.html', posts=posts_list)
    

@home_bp.route('/m')
def mobile_index():
    db = SQLighter(db_uri)
    if 'username' in session:
        db.update_last_seen(session['username'])

    # Вызываем функцию get_posts() непосредственно, без HTTP-запроса
    posts_response = apiv1.get_posts()  # Здесь предполагается, что get_posts возвращает ответ Flask

    # Получаем список постов из ответа
    posts_list = posts_response.json.get('posts', []) if hasattr(posts_response, 'json') else []
    return render_template('mobile_index.html', posts=posts_list)