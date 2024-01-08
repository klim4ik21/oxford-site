from flask import Blueprint
from data.db import SQLighter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    db = SQLighter(db_uri)
    if 'username' in session:
        db.update_last_seen(session['username'])
    posts = db.get_posts()
    posts_list = []
    for post in posts:
        post_dict = {
            'id': post[0],
            'text': post[1],
            'image_name': post[2],
            'created_at': post[3],
            'head_title': post[5],
            'username': post[6],
            'post_owner_id': post[7]
        }
        post_photo_name = post_dict['image_name']
        post_dict['full_image_url'] = get_full_image_url(post_photo_name)
        posts_list.append(post_dict)

    return render_template('index.html', posts=posts_list)