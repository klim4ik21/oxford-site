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
    
    def get_posts(self):
        self.cursor.execute('''
            SELECT posts.id, posts.text, posts.image_url, posts.created_at, users.username, posts.head_title
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


        
    def create_post(self, text, image_url, head_title, username):
        query = '''
        INSERT INTO posts (text, user_id, image_url, created_at, head_title, username) 
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s)

        '''
        try:
            print("ПОСТ УСПЕШНО СОЗДАН")
            self.cursor.execute(query, (text, 3, image_url, head_title, username))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при создании поста: {e}")
            self.connection.rollback()
            return False