from flask import Flask,render_template
from books import all_books

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

