from flask import Blueprint, render_template, redirect, request, url_for, jsonify
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/add_friend/<int:user_id2>', methods=['POST'])
def add_friend(user_id2):
    if 'username' in session:
        db = SQLighter(db_uri)
        user1 = db.get_user(session['username'])  # ID пользователя, отправляющего запрос
        db.update_friend(sender_id=user1[0], to_user_id=user_id2, status='send')
        return jsonify({'status': 'request_sent'})
    
@friends_bp.route('/respond_friend_request/<int:request_id>', methods=['POST'])
def respond_friend_request(request_id):
    response = request.form['response']  # 'accepted' или 'declined'
    if 'username' in session:
        db = SQLighter(db_uri)
        if response == 'accepted' or response == 'declined':
            db.update_friend(sender_id=request_id, to_user_id=None, status=f'{response}')

    return redirect(url_for('profile_bp.profile'))