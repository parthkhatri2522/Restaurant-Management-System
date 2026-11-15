import os

from flask import Flask, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config import Config
from app.extensions import db, migrate


def create_app():

    # Initialize Flask application
    app = Flask(
        __name__,
        instance_relative_config=True
    )

    # Load application configuration
    app.config.from_object(Config)

    # Create instance directory automatically
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Backend health-check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():

        return jsonify({
            "status": "success",
            "message": "ServeWise backend is running"
        }), 200

    # Database connection health-check endpoint
    @app.route("/health/database", methods=["GET"])
    def database_health_check():

        try:
            db.session.execute(text("SELECT 1"))

            return jsonify({
                "status": "success",
                "message": "Database connection successful"
            }), 200

        except SQLAlchemyError:

            db.session.rollback()

            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

    return app