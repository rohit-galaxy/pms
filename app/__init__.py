import sys
import os
import mysql.connector.pooling
from flask import Flask

# Fix sys.path for config import (keep this if needed)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

cnxpool = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    global cnxpool
    cnxpool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
    )

    # Register blueprints
    from app.controllers.category_controller import category_bp
    from app.controllers.brand_controller import brand_bp
    from app.controllers.product_controller import product_bp

    app.register_blueprint(category_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(product_bp)

    return app

def get_connection():
    global cnxpool
    return cnxpool.get_connection()
