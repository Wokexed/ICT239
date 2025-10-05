# helps python to recognize this folder as a software

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    # app.secret_key = "your_secret_key"
    app.config["SECRET_KEY"] = "1c31274a526e7db696122ffea8a95f76"

    app.config["MONGODB_SETTINGS"] = {
        "db": "shopping_app_db",
        "host": "localhost",
        "port": 27017
    }

    db = MongoEngine(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"  # Redirect to 'login' view if not logged in 

    return app, db, login_manager

app, db, login_manager = create_app()