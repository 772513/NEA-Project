from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import sqlalchemy as sa
import sqlalchemy.orm as so
from config import Config

# define extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # initiate extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    login.login_view = 'main.login'

    # main is a blueprint defined in routes.py cointaing all the route definitions for that specific part of the app
    # create_app() imports and registers the blueprint to the app after the app instance is created,
    # this prevents circular imports
    from app.routes import main
    from app.models import User, Match
    from app import models

    @app.shell_context_processor
    def make_shell_context():
        return {"sa": sa, "so": so, "db": db, "User": User, "Match": Match}

    app.register_blueprint(main)

    return app
