from flask import Flask
from .extensions import db
from .controllers.auth_controller import auth_bp
from .controllers.expense_controller import expense_bp
from .controllers.recurring_expenses_controller import recurring_bp
from .config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Override the database URI with SSL
    DATABASE_URL = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "require"}}

    db.init_app(app)  # MUST be called
    app.register_blueprint(auth_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(recurring_bp)

    return app
