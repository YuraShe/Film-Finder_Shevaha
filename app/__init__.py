from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from datetime import timedelta

from . import config

db = SQLAlchemy()
BASE_DIR = Path(__file__).resolve().parent.parent


def create_app() -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_AS_ASCII"] = False
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)

    db.init_app(app)

    # Register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route("/")
    def index():
        """Render the main chat interface page."""
        return render_template("index.html")

    return app