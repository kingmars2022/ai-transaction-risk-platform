from flask import Flask
from .config import Config
from .extensions import db
from .routes import api

def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)
    db.init_app(app)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    return app
