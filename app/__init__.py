from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # main is a blueprint defined in routes.py cointaing all the route definitions for that specific part of the app
    # create_app() imports and registers the blueprint to the app after the app instance is created,
    # this prevents circular imports
    from app.routes import main

    app.register_blueprint(main)

    return app
