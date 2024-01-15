from flask import Blueprint, render_template, redirect, request, url_for, jsonify, flash, abort
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash
from api_v1 import v1 as apiv1
import utils

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/im')
def conversations():
    db = SQLighter(db_uri=db_uri)
    user = db.get_user(session['username'])
    return render_template('im.html', currentUserId=user[0], username=user[1])

@messages_bp.route('/im/<int:other_user_id>')
def conversation_with_user(other_user_id):
    db = SQLighter(db_uri=db_uri)
    current_username = session.get('username')  # Имя пользователя из сессии
    current_user = db.get_user(current_username)
    #avatar = utils.get_full_image_url(current_user[6])
    if not current_user:
        abort(404, "Текущий пользователь не найден")

    current_user_id = current_user['id']
    conversation_id = db.get_conversation_id(current_user_id, other_user_id)

    if not conversation_id:
        # Если чата не существует, создаем новый
        conversation_id = db.create_conversation(current_user_id, other_user_id)

    return render_template('user_im.html', conversation_id=conversation_id, username=current_user[1], other_user_id=other_user_id)
