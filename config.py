import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Config:
	SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

	# MySQL connection string example: mysql+pymysql://user:password@localhost:3306/dbname
	SQLALCHEMY_DATABASE_URI = os.getenv(
		"DATABASE_URL",
		"mysql+pymysql://root:password@localhost:3306/flask_rbac_db",
	)
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Flask-Migrate settings (optional)
	DB_SCHEMA_NAME = os.getenv("DB_SCHEMA_NAME", "flask_rbac_db")


class TestConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.getenv(
		"TEST_DATABASE_URL",
		"sqlite+pysqlite:///:memory:",
	)

