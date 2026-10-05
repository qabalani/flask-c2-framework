from flask import Flask
from config import Config
from c2.database import init_db
from c2.routes_api import api_bp
from c2.routes_dashboard import dash_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    app.register_blueprint(api_bp)
    app.register_blueprint(dash_bp)
    return app
