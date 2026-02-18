import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions (DO NOT move inside function)
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name=None):
    """
    Application Factory
    """

    from app.config import config

    # Read config from environment variable
    if not config_name:
        config_name = os.getenv("CONFIG_NAME", "development")

    app = Flask(__name__)

    # Safety fallback
    if config_name not in config:
        config_name = "development"

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Enable CORS (allow frontend connection)
    CORS(
        app,
        resources={r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }}
    )

    # Register blueprints
    with app.app_context():
        from app.routes import auth_bp, upload_bp, analysis_bp, results_bp

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(upload_bp, url_prefix='/api/upload')
        app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
        app.register_blueprint(results_bp, url_prefix='/api/results')

        # Create database tables
        try:
            db.create_all()
            print("✓ Database tables created/verified")
        except Exception as e:
            print(f"⚠ Database creation warning: {e}")

    return app
