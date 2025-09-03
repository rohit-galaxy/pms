import os
import mysql.connector.pooling
from flask import Flask, session, redirect, url_for, request, flash
from functools import wraps

cnxpool = None

def login_required(f):
    """Decorator to ensure the user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or not session.get("is_authenticated"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth_bp.login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """Decorator to ensure the user has the required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session or not session.get("is_authenticated"):
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth_bp.login"))

            # Check admin role with is_admin boolean flag
            if role == "admin" and not session.get("is_admin", False):
                flash("You are not authorized to access this page.", "danger")
                return redirect(url_for("product_bp.index"))  # send normal users to their dashboard

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    global cnxpool
    cnxpool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
    )

    # Blueprint imports
    from app.controllers.auth_controller import auth_bp
    from app.controllers.product_controller import product_bp
    from app.controllers.category_controller import category_bp
    from app.controllers.brand_controller import brand_bp
    from app.controllers.user_controller import user_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(product_bp, url_prefix="/products")
    app.register_blueprint(category_bp, url_prefix="/categories")
    app.register_blueprint(brand_bp, url_prefix="/brands")
    app.register_blueprint(user_bp, url_prefix="/users")

    # Expose decorators for use in controllers
    app.login_required = login_required
    app.role_required = role_required

    @app.route('/')
    def index():
        # Home redirects to login by default
        return redirect(url_for('auth_bp.login'))

    @app.before_request
    def enforce_login():
        """Force login except for auth routes and static files"""
        if request.endpoint:
            if request.endpoint.startswith("auth_bp.") or request.endpoint.startswith("static"):
                return  # allow
        if "user_id" not in session or not session.get("is_authenticated"):
            return redirect(url_for("auth_bp.login"))

    return app

def get_connection():
    global cnxpool
    return cnxpool.get_connection()
