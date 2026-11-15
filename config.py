import os


class Config:

    # Application security configuration
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "servewise-development-secret"
    )

    # Enable debug mode during development
    DEBUG = True