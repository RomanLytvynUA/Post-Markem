from flask import Flask
from .routes.events import events_bp
from .routes.main import main_bp
from .routes.categories import categories_bp
from .routes.people import people_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(events_bp, url_prefix='/events/')
    app.register_blueprint(categories_bp, url_prefix='/categories/')
    app.register_blueprint(people_bp, url_prefix='/people/')
    app.register_blueprint(main_bp)

    return app