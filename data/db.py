import psycopg2
import datetime
from psycopg2.extras import DictCursor
import boto3
from botocore.client import Config

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
    
    def get_posts(self):
        self.cursor.execute('''
            SELECT posts.id, posts.text, posts.image_url, posts.created_at, users.username
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
        ''')
        return self.cursor.fetchall()
    
    def find_photo(bucket_name, photo_name):
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=photo_name)

        if 'Contents' in response:
            photos = [item['Key'] for item in response['Contents']]
            return photos
        else:
            return []