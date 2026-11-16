
import os
import click

from flask import Flask, jsonify
from flask_login import current_user, LoginManager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config import Config
from app.extensions import db, migrate, login_manager


def create_app():

    app = Flask(
        __name__,
        instance_relative_config=True
    )

    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.session_protection = "strong"

    # Import database models
    from app.models import User, Employee

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    # Initialize migrations
    migrate.init_app(app, db)

    # Register authentication routes
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Register role-based access routes
    from app.routes.access import access_bp
    app.register_blueprint(access_bp)

    # Backend health check
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "success",
            "message": "ServeWise backend is running"
        }), 200

    # Database health check
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

    # Initial administrator creation command
    @app.cli.command("create-admin")
    def create_admin():

        username = click.prompt("Administrator username")
        email = click.prompt("Administrator email")

        password = click.prompt(
            "Administrator password",
            hide_input=True,
            confirmation_prompt=True
        )

        if len(password) < 8:
            raise click.ClickException(
                "Password must contain at least 8 characters"
            )

        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:
            raise click.ClickException(
                "Username or email already exists"
            )

        admin = User(
            username=username,
            email=email,
            role="system_administrator",
            is_active=True
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        click.echo("Administrator account created successfully!")

    return app
