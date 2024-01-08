import psycopg2
import datetime
from psycopg2.extras import DictCursor
import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError
from werkzeug.utils import secure_filename

s3 = boto3.client(
    's3',
    endpoint_url='https://s3.timeweb.com',
    region_name='ru-1',
    aws_access_key_id='cb42813',
    aws_secret_access_key='488554bbf25da342105ef70286f08971',
    config=Config(signature_version='s3v4')
)

db_uri = "postgresql://gen_user:q%2Fgy%3FQy%3F0%3Dfi%5C%3F@109.172.88.61:5432/default_db"

class SQLighter:
    def __init__(self, db_uri):
        self.connection = psycopg2.connect(db_uri)
        self.cursor = self.connection.cursor()
        
    def create_user(self, username, password_hash, email):
        # Добавление нового пользователя в базу данных
        self.cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)', (username, password_hash, email))
        self.connection.commit()

    def get_user(self, username):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            return cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()
    
    def get_posts(self):
        self.cursor.execute('''
            SELECT posts.id, posts.text, posts.image_url, posts.created_at, users.username, posts.head_title, posts.username, posts.post_owner_id
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
        ''')
        return self.cursor.fetchall()
    
    def find_photo(self, photo_name):
        response = s3.list_objects_v2(Bucket="1f38301d-d3dcd88d-0a80-4ad8-981a-5aa4655a891b", Prefix=photo_name)

        if 'Contents' in response:
            photos = [item['Key'] for item in response['Contents']]
            try:
                response_photo = s3.generate_presigned_url('get_object',
                                                            Params={'Bucket': "1f38301d-d3dcd88d-0a80-4ad8-981a-5aa4655a891b",
                                                                    'Key': photos[0]},
                                                            ExpiresIn=3600)
            except NoCredentialsError:
                print("Ошибка учетных данных")
                return None
            return response_photo
        else:
            return "Cant Load photo"
        
    def update_last_seen(self, username):
        current_time = datetime.datetime.now()
        self.cursor.execute('UPDATE users SET last_seen = %s WHERE username = %s', (current_time, username))
        self.connection.commit()

    def get_last_seen(self, username):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT last_seen FROM users WHERE username = %s', (username,))
            result = cursor.fetchone()
            return result['last_seen']


    def get_user_by_id(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()


    def is_online(self, last_seen):
        if last_seen:
            return (datetime.datetime.now() - last_seen) < datetime.timedelta(minutes=5)
        return False
    
    def update_avatar(self, file, user_id):
        filename = f'avatar_{user_id}_{file.filename}'
        self.upload_to_s3v2(file, filename=filename)
        self.cursor.execute('UPDATE users SET img_avatar = %s WHERE id = %s', (filename, user_id))
        self.connection.commit()

    def get_avatar(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT img_avatar FROM users WHERE id = %s', (user_id,))
            result = cursor.fetchone()
            if result and result['img_avatar']:
                print(f"!!! {result['img_avatar']}")
                avatar_name = result['img_avatar']
                return self.find_photo(avatar_name)
            else:
                return None  # Или URL изображения по умолчанию, если аватар отсутствует

        
    def upload_to_s3(self, file):
        try:
            # Получаем имя файла из объекта file
            filename = secure_filename(file.filename)
            print(f"Начинается загрузка файла: {filename}")

            # Загружаем файл на S3
            s3.upload_fileobj(
                file,   
                "1f38301d-d3dcd88d-0a80-4ad8-981a-5aa4655a891b",
                filename
            )
            print(f"Файл успешно загружен: {filename}")
            return filename
        except Exception as error:
            print(f"Ошибка при загрузке файла: {error}")
            return
        
    def upload_to_s3v2(self, file, filename):
        try:
            print(f"v2 Начинается загрузка файла: {filename}")

            # Загружаем файл на S3
            s3.upload_fileobj(
                file,   
                "1f38301d-d3dcd88d-0a80-4ad8-981a-5aa4655a891b",
                filename
            )
            print(f"Файл успешно загружен: {filename}")
            return filename
        except Exception as error:
            print(f"Ошибка при загрузке файла: {error}")
            return
        
    def create_post(self, text, image_url, head_title, username, post_owner_id):
        query = '''
        INSERT INTO posts (text, user_id, image_url, created_at, head_title, username, post_owner_id) 
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s)

        '''
        try:
            print("ПОСТ УСПЕШНО СОЗДАН")
            self.cursor.execute(query, (text, 3, image_url, head_title, username, post_owner_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при создании поста: {e}")
            self.connection.rollback()
            return False
        
    def update_friend(self, sender_id, to_user_id, status):
        if status == 'send':
            self.cursor.execute('INSERT INTO friends (user_id1, user_id2, status) VALUES (%s, %s, %s)', (sender_id, to_user_id, 'pending'))
            self.connection.commit()
        elif status == 'accepted':
            self.cursor.execute('UPDATE friends SET status = %s WHERE id = %s', ('accepted', sender_id))
            self.connection.commit() 

    def get_friend_requests(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            query = """
            SELECT u.id as user_id, u.username as sender_username, f.id as request_id
            FROM friends f
            JOIN users u ON f.user_id1 = u.id
            WHERE f.user_id2 = %s AND f.status = 'pending'
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        
    def get_friends(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            # This query fetches the user IDs of friends.
            query = """
            SELECT f.user_id1, f.user_id2
            FROM friends f
            WHERE (f.user_id1 = %s OR f.user_id2 = %s) AND f.status = 'accepted'
            """
            cursor.execute(query, (user_id, user_id))
            rows = cursor.fetchall()
        
        # Now fetch the usernames using the get_user_by_id function
        friend_usernames = []
        for row in rows:
            # Check which user_id is the friend's ID and get their username
            friend_id = row['user_id1'] if row['user_id2'] == user_id else row['user_id2']
            friend_info = self.get_user_by_id(friend_id)
            if friend_info:
                friend_usernames.append(friend_info['username'])
        print(friend_usernames)
        return friend_usernames