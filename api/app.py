from flask import Flask
from api.extensions import db, migrate, jwt
from api.views.views import api_bp


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    configure_extensions(app)
    configure_jwt(app)
    app.register_blueprint(api_bp, url_prefix="/api")  # localhost/api/

    return app


def configure_extensions(app):
    """configure flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)


def configure_jwt(app):
    jwt.init_app(app)
