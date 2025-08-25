import sys
import os
import mysql.connector.pooling
from flask import Flask
from .extensions import db, login_manager, bcrypt, migrate
from config import Config

# Fix sys.path for config import (keep this if needed)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

cnxpool = None

def create_app(config_class: type[Config] = Config) -> Flask:
	app = Flask(__name__, template_folder="templates", static_folder="static")
	app.config.from_object(config_class)

	global cnxpool
	cnxpool = mysql.connector.pooling.MySQLConnectionPool(
		pool_name="mypool",
		pool_size=5,
		host=app.config["MYSQL_HOST"],
		user=app.config["MYSQL_USER"],
		password=app.config["MYSQL_PASSWORD"],
		database=app.config["MYSQL_DB"],
	)

	# Initialize extensions
	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	migrate.init_app(app, db)

	# Register blueprints
	from .blueprints.auth.routes import auth_bp
	from .blueprints.catalog.routes import catalog_bp
	from .blueprints.admin.routes import admin_bp

	app.register_blueprint(auth_bp)
	app.register_blueprint(catalog_bp, url_prefix="/catalog")
	app.register_blueprint(admin_bp, url_prefix="/admin")

	# Simple index route
	@app.route("/")
	def index():
		from flask_login import current_user
		from flask import redirect, url_for

		if current_user.is_authenticated:
			if current_user.is_admin:
				return redirect(url_for("admin.dashboard"))
			return redirect(url_for("catalog.user_dashboard"))
		return redirect(url_for("auth.login"))

	return app

def get_connection():
    global cnxpool
    return cnxpool.get_connection()
