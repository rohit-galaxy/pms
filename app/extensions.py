from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Extensions are instantiated here and initialized in app factory

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

# Where to redirect for @login_required
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"