from flask import Blueprint, render_template, redirect, request, url_for, jsonify
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash
import utils

posts_bp = Blueprint('posts', __name__)


@posts_bp.route('/create_post', methods=['POST'])
def create_post():
    if 'username' in session:
        db = SQLighter(db_uri)
        user_info = db.get_user(session['username'])
        head_title = request.form['head_title']
        post_text = request.form['post_text']
        post_image = request.files['post_image']
        if post_image:
            image_url = utils.upload_to_s3(file=post_image)
            create_post = db.create_post(username=session['username'], text=post_text, image_url=image_url, head_title=head_title, post_owner_id=user_info[0]) == True
            if create_post:
                return "пост успешно опубликован"
            else:
                return create_post

        return redirect(url_for('home.home'))
    else:
        return 'Произошла ошибка: вы не авторизованы', 'auth error'
    
@posts_bp.route('/create_comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    db = SQLighter(db_uri)
    # Получение текста комментария из формы
    comment_text = request.form.get('comment_text')
    # Получение ID пользователя (например, из сессии)
    user_id = db.get_user(session.get('username'))

    db.add_comment(post_id, comment_text, user_id[0])

    return redirect(url_for('home.home'))
