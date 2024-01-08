from flask import Blueprint, render_template, redirect, request, url_for, jsonify
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash

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
            image_url = db.upload_to_s3(post_image)
            create_post = db.create_post(username=session['username'], text=post_text, image_url=image_url, head_title=head_title, post_owner_id=user_info[0]) == True
            if create_post:
                return "пост успешно опубликован"
            else:
                return create_post

        return redirect(url_for('home_bp.home'))
    else:
        return 'Произошла ошибка: вы не авторизованы', 'auth error'