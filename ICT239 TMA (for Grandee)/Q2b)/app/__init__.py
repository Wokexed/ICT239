from flask import Flask
from flask_mongoengine import MongoEngine

db = MongoEngine()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key'
    app.config['MONGODB_SETTINGS'] = {
        'db': 'library_db',
        'host': '127.0.0.1',
        'port': 27017
    }
    db.init_app(app)

    return app

app = create_app()