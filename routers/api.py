from flask import Blueprint, render_template, redirect, request, url_for, jsonify, flash
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash
from api_v1 import v1 as apiv1

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/api/<string:method>')
def api_callback(method):
    # Check if the user is logged in
    if 'username' in session and session['username']:
        # Get User Method
        if method == 'get_user':
            user_id = request.args.get('user_id', type=int)
            if user_id is not None:
                return apiv1.get_user(user_id)
            else:
                return jsonify({"error": "Missing user_id"}), 400
        # GetPosts Method
        elif method == 'get_posts':
            return apiv1.get_posts(user_id)
        # GetUserPosts Method
        elif method == 'get_user_posts':
            user_id = request.args.get('user_id', type=int)
            if user_id is not None:
                return apiv1.get_user_posts(user_id)
            
            else:
                return jsonify({"error": "Missing user_id"}), 400
        # You can add more methods here
        else:
            return jsonify({"error": "API METHOD ERROR"}), 400
    else:
        return jsonify({"error": "Unauthorized: No active session"}), 401