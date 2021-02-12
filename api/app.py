from flask import Flask
from api.extensions import db
from api.views.views import api_bp


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    db.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")  # localhost/api/

    return app
