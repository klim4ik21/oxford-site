from config import db_uri
import datetime
from data.db import SQLighter
import json
from flask import jsonify
import utils

def get_user(user_id):
    db = SQLighter(db_uri)
    user_info = db.get_user_by_id(user_id=user_id)

    if user_info:
        avatar = db.get_avatar(user_info[0])
        # Convert user_info to a dictionary and exclude the password hash
        user_dict = {
            'id': user_info[0],
            'username': user_info[1],
            'email': user_info[3],
            'created_at': user_info[4],
            'last_seen': user_info[5],
            'img_avatar': avatar,
            # include other fields as needed, but exclude the password hash
        }
        return jsonify({'user': user_dict})
    else:
        return jsonify({"error": "User not found"}), 404
    
def get_posts():
    db = SQLighter(db_uri)
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
            'post_owner_id': post[7],
            'comments': db.get_comments(post[0])  # Извлекаем комментарии для каждого поста
        }

        post_photo_name = post_dict['image_name']
        post_dict['full_image_url'] = utils.get_full_image_url(post_photo_name)
        posts_list.append(post_dict)

    return jsonify(posts=posts_list)


    
def get_user_posts(user_id):
    db = SQLighter(db_uri)
    posts = db.get_posts_by_id(user_id=user_id)
    posts_list = []

    for post in posts:
        post_dict = {
            'id': post[0],
            'text': post[1],
            'image_name': post[2],
            'created_at': post[3],
            'head_title': post[5],
            'username': post[6],
            'post_owner_id': post[7],
            'comments': db.get_comments(post[0])  # Извлекаем комментарии для каждого поста
        }

        post_photo_name = post_dict['image_name']
        post_dict['full_image_url'] = utils.get_full_image_url(post_photo_name)
        posts_list.append(post_dict)

    return jsonify(posts=posts_list)

def get_post_comments(post_id):
    db = SQLighter(db_uri)
    comments = db.get_comments(post_id=post_id)
    return jsonify(comments)