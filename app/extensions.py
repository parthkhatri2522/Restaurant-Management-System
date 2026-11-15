from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy database extension
db = SQLAlchemy()

# Initialize database migration extension
migrate = Migrate()