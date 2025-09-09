# helps python to recognize this folder as a software

from flask import Flask
from flask_mongoengine import MongoEngine

def create_app():
    app = Flask(__name__)
    # app.secret_key = "your_secret_key"
    app.config["SECRET_KEY"] = "your_secret_key"

    app.config["MONGODB_SETTINGS"] = {
        "db": "shopping_app_db",
        "host": "localhost",
        "port": 27017
    }

    db = MongoEngine(app)
    return app, db

app, db = create_app()