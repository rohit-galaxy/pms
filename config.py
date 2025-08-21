import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "123"
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "Admin@123"
    MYSQL_DB = "product_db"
    MYSQL_CURSORCLASS = "DictCursor"

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB upload limit

