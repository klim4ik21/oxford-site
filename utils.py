from data.db import SQLighter
from config import db_uri

def get_full_image_url(image_path):
    if image_path:
        db = SQLighter(db_uri)
        print(db.find_photo(photo_name=image_path))
        return db.find_photo(photo_name=image_path)
    return None