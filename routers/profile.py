from flask import Blueprint, render_template, redirect, request, url_for, jsonify
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash
import utils

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    db = SQLighter(db_uri)
    if 'username' in session:
        username = session['username']
        user_info = db.get_user(username)
        user_id = user_info['id']  # Ensure this matches your data structure
        last_seen = db.get_last_seen(username)
        online_status = db.is_online(last_seen)
        avatar = db.get_avatar(user_id)
        friend_requests = db.get_friend_requests(user_id)
        friend_usernames = db.get_friends(user_id)
        # Debugging: Print the friend_requests to see the structure
        print(friend_requests)

        return render_template('profile.html', user=user_info, is_online=online_status, avatar=avatar, friend_requests=friend_requests, friends=friend_usernames)
    else:
        return redirect(url_for('login_bp.login'))
    

@profile_bp.route('/img_update_avatar', methods=['POST'])
def img_avatar_update():
    if 'username' in session:
        db = SQLighter(db_uri)
        user_info = db.get_user(session['username'])
        avatar = request.files['img_avatar']
        db.update_avatar(avatar, user_info[0])
        return redirect(url_for('home_bp.home'))