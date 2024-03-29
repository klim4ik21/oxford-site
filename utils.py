from config import db_uri
import datetime
import boto3
from botocore.client import Config
from werkzeug.utils import secure_filename

s3 = boto3.client(
    's3',
    endpoint_url='https://s3.timeweb.com',
    region_name='ru-1',
    aws_access_key_id='some data',
    aws_secret_access_key='access_key',
    config=Config(signature_version='s3v4')
)

def file_exists_in_s3(key):
    try:
        s3.head_object(Bucket='1f38301d-d3dcd88d-0a80-4ad8-981a-5aa4655a891b', Key=key)
        return True
    except s3.exceptions.ClientError as e:
        # Если объекта не существует, будет вызвано исключение ClientError
        return False


def find_s3(photo_name):
        response = file_exists_in_s3(photo_name)
        start_timer = datetime.datetime.now()
        if response:
            response_photo = s3.generate_presigned_url('get_object',
                                                        Params={'Bucket': "1f38301d-d3dcd88d-0a80-4ad8-981a-5aa4655a891b",
                                                                'Key': photo_name},
                                                        ExpiresIn=3600)
            end_timer = datetime.datetime.now()
            print(end_timer - start_timer)
            return response_photo
        else:
            return "Cant Load photo"

def get_full_image_url(image_path):
    if image_path:
        start_timer = datetime.datetime.now()
        print()
        print('photo loaded')
        photo = find_s3(photo_name=image_path)
        end_timer = datetime.datetime.now()
        print(f'GET FULL IMAGE URL{end_timer - start_timer}')
        return photo
    return None

        
def upload_to_s3v2(self, file, filename):
    try:

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
    
def upload_to_s3(file):
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
