from flask import Blueprint, render_template, redirect, request, url_for, jsonify, flash
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash
from api_v1 import v1 as apiv1

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/api/<string:method>', methods=['POST', 'GET'])
def api_callback(method):
    # Check if the user is logged in
    if 'username' in session and session['username'] or method != 'get_post_methods':
        # Get User Method
        if method == 'get_user':
            user_id = request.args.get('user_id', type=int)
            if user_id is not None:
                return apiv1.get_user(user_id)
            else:
                return jsonify({"error": "Missing user_id"}), 400
        # GetPosts Method
        elif method == 'get_posts':
            return apiv1.get_posts()
        # GetUserPosts Method
        elif method == 'get_user_posts':
            user_id = request.args.get('user_id', type=int)
            if user_id is not None:
                return apiv1.get_user_posts(user_id)
            else:
                return jsonify({"error": "Missing user_id"}), 400
        # You can add more methods here
        elif method == 'get_post_comments':
            post_id = request.args.get('post_id', type=int)
            if post_id is not None:
                return apiv1.get_post_comments(post_id)
            else:
                return jsonify({"error": "Missing post_id"}), 400
        elif method == 'get_conversations':
            db = SQLighter(db_uri)
            user = db.get_user(session['username'])
            return apiv1.get_conversations(user[0])
        elif method == 'get_messages':
            conversation_id = request.args.get('conversation_id', type=int)
            return apiv1.get_messages(conversation_id=conversation_id)
        elif method == 'send_message':
            data = request.get_json()
            db = SQLighter(db_uri)
            user = db.get_user(session['username'])
            conversation_id = data['conversation_id']
            message_text = data['text']
            return apiv1.send_message(conversation_id=conversation_id, sender_id=user[0], message_text=message_text)
        elif method == 'mark_message_as_read':
            message_id = request.args.get('message_id')
            return apiv1.mark_message_as_read(message_id=message_id)
        else:
            return jsonify({"error": "API METHOD ERROR"}), 400
    else:
        return jsonify({"error": "Unauthorized: No active session"}), 401