from data.db import SQLighter
from config import db_uri
import datetime
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