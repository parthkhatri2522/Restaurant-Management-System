from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize database extension
db = SQLAlchemy()

# Initialize database migration extension
migrate = Migrate()

# Initialize authentication manager
login_manager = LoginManager()