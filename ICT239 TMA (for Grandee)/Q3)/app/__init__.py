from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

db = MongoEngine()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'e6f2d7a56e67c2e56343a6004dd62f71'
    app.config['MONGODB_SETTINGS'] = {
        'db': 'library_db',
        'host': '127.0.0.1',
        'port': 27017
    }
    db.init_app(app)
    login_manager = LoginManager(app)

    return app, login_manager

app, login_manager = create_app()