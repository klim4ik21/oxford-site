from flask import Blueprint, render_template, redirect, request, url_for
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash

reg_bp = Blueprint('register', __name__)

@reg_bp.route('/register', methods=['GET', 'POST'])
def register():
    db = SQLighter(db_uri)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']  # Получение email из формы
        password_hash = generate_password_hash(password)
        db.create_user(username, password_hash, email)
        return redirect(url_for('home.home'))
    return render_template('register.html')