from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from data.db import SQLighter
from werkzeug.security import generate_password_hash, check_password_hash
from config import db_uri


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
        username = session['username']
        user_info = db.get_user(username)
        last_seen = db.get_last_seen(username)
        online_status = db.is_online(last_seen)
        avatar = db.get_avatar(user_info[0])
        print(avatar)
        return render_template('profile.html', user=user_info, is_online=online_status, avatar=avatar)
    else:
        return redirect(url_for('login'))
    
@app.route('/img_update_avatar', methods=['POST'])
def img_avatar_update():
    if 'username' in session:
        db = SQLighter(db_uri)
        user_info = db.get_user(session['username'])
        avatar = request.files['img_avatar']
        db.update_avatar(avatar, user_info[0])
        return redirect(url_for('home'))

@app.route('/create_post', methods=['POST'])
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
                flash("пост успешно опубликован")
            else:
                flash(create_post)

        return redirect(url_for('home'))
    else:
        flash('Произошла ошибка: вы не авторизованы', 'auth error')

@app.route('/users/<int:user_id>')
def view_profile(user_id):
    db = SQLighter(db_uri)
    user_info = db.get_user_by_id(user_id)
    avatar = db.get_avatar(user_id)
    if user_info:
        print(user_info[1])
        last_seen = db.get_last_seen(user_info[1])
        online_status = db.is_online(last_seen)
        print(online_status)
        return render_template('user_profile.html', user=user_info, is_online=online_status, avatar=avatar)
    else:
        flash('Пользователь не найден')
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
