from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from data.db import SQLighter
from werkzeug.security import generate_password_hash, check_password_hash
from config import db_uri
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = '111'

# Настройка Flask-Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_full_image_url(image_path):
    if image_path:
        db = SQLighter(db_uri)
        print(db.find_photo(photo_name=image_path))
        return db.find_photo(photo_name=image_path)
    return None

@app.route('/')
def home():
    db = SQLighter(db_uri)
    posts = db.get_posts()
    posts_list = []
    for post in posts:
        post_dict = {
            'id': post[0],
            'text': post[1],
            'image_name': post[2],
            'created_at': post[3],
            'username': post[4]
        }
        post_photo_name = post_dict['image_name']
        post_dict['full_image_url'] = get_full_image_url(post_photo_name)
        posts_list.append(post_dict)

    return render_template('index.html', posts=posts_list)
    # if 'username' in session:
    #     return render_template('index.html', username=session['username'], posts=posts)
    # else:
    #     return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    db = SQLighter(db_uri)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']  # Получение email из формы
        password_hash = generate_password_hash(password)
        db.create_user(username, password_hash, email)
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = SQLighter(db_uri)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Здесь должна быть ваша логика проверки учетных данных
        user = db.get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            return redirect(url_for('home'))  # Перенаправление на главную страницу после входа
        else:
            # Если учетные данные неверны, показать сообщение об ошибке
            print("Some error!")
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/profile')
def profile():
    db = SQLighter(db_uri)
    if 'username' in session:
        user_info = db.get_user(session['username'])
        return render_template('profile.html', user=user_info)
    else:
        return redirect(url_for('login'))
    
@app.route('/create_post', methods=['POST'])
def create_post():
    post_text = request.form['post_text']
    post_image = request.files['post_image']
    
    # Здесь должен быть код для обработки и сохранения поста и изображения
    # ...

    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
