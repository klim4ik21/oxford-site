from config import db_uri
import datetime
from data.db import SQLighter
import json
from flask import jsonify



from flask import jsonify

def get_user(user_id):
    db = SQLighter(db_uri)
    user_info = db.get_user_by_id(user_id=user_id)

    if user_info:
        # Convert user_info to a dictionary and exclude the password hash
        user_dict = {
            'id': user_info[0],
            'username': user_info[1],
            'email': user_info[3],
            'created_at': user_info[4],
            'last_seen': user_info[5],
            # include other fields as needed, but exclude the password hash
        }
        return jsonify({'user': user_dict})
    else:
        return jsonify({"error": "User not found"}), 404
