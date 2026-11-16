import os


class Config:

    # Application security configuration
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "servewise-development-secret"
    )

    # SQLite database configuration
    SQLALCHEMY_DATABASE_URI = "sqlite:///servewise.db"

    # Disable unnecessary modification tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Enable debugging during development
    DEBUG = True