import sys
import os
import mysql.connector.pooling
from flask import Flask, g, session
from config import Config
from .extensions import db, migrate

# Fix sys.path for config import (keep this if needed)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

cnxpool = None

def create_app() -> Flask:
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(Config)

    # Init extensions (SQLAlchemy optional in current raw-SQL usage)
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.controllers.category_controller import category_bp
    from app.controllers.brand_controller import brand_bp
    from app.controllers.product_controller import product_bp
    from .blueprints.auth.routes import auth_bp
    from .blueprints.users.routes import users_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(category_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(product_bp)

    @app.before_request
    def load_current_user():
        user_id = session.get("user_id")
        is_admin = session.get("is_admin", False)
        if user_id is not None:
            g.current_user_id = user_id
            g.current_user_is_admin = bool(is_admin)
        else:
            g.current_user_id = None
            g.current_user_is_admin = False

    @app.get("/")
    def index():
        from flask import redirect, url_for
        if session.get("user_id"):
            if session.get("is_admin"):
                return redirect(url_for("users_bp.index"))
            return redirect(url_for("product_bp.index"))
        return redirect(url_for("auth_bp.login_page"))

    return app

def get_connection():
    global cnxpool
    if cnxpool is None:
        # Lazy initialize the pool to avoid failing app startup when DB is down
        cnxpool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
        )
    return cnxpool.get_connection()
