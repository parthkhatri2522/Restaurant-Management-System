import os

from flask import Flask, jsonify

from config import Config


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

    # Backend health-check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():

        return jsonify({
            "status": "success",
            "message": "ServeWise backend is running"
        }), 200

    return app