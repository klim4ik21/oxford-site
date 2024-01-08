from flask import Blueprint, render_template, redirect, request, url_for, jsonify
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users', __name__)

@users_bp.route('/users/<int:user_id>')
def view_profile(user_id):
    db = SQLighter(db_uri)
    user_info = db.get_user_by_id(user_id)
    avatar = db.get_avatar(user_id)
    if user_info:
        print(user_info[1])
        last_seen = db.get_last_seen(user_info[1])
        online_status = db.is_online(last_seen)
        print(online_status)
        return render_template('user_profile.html', user=user_info, is_online=online_status, avatar=avatar)
    else:
        return redirect(url_for('home_bp.home'))