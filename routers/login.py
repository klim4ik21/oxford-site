from flask import Blueprint, render_template, redirect, request, url_for, flash
from data.db import SQLighter
from flask import session
from config import db_uri
from werkzeug.security import generate_password_hash, check_password_hash

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    db = SQLighter(db_uri)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Здесь должна быть ваша логика проверки учетных данных
        user = db.get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            flash("Success", category='success')
            return redirect(url_for('home.home'))  # Перенаправление на главную страницу после входа
        else:
            # Если учетные данные неверны, показать сообщение об ошибке
            flash("Invalid Username or Password", category='warning')
            return redirect(url_for('login.login'))

    return render_template('login.html')

@login_bp.route('/mlogin', methods=['GET', 'POST'])
def mlogin():
    db = SQLighter(db_uri)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Здесь должна быть ваша логика проверки учетных данных
        user = db.get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            flash("Success", category='success')
            return redirect(url_for('home.home'))  # Перенаправление на главную страницу после входа
        else:
            # Если учетные данные неверны, показать сообщение об ошибке
            flash("Invalid Username or Password", category='warning')
            return redirect(url_for('login.mlogin'))

    return render_template('mobile_login.html')

@login_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home.home'))