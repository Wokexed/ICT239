#!/bin/bash

# 1. Activate the Python Virtual Environment (Linux/Bash command)
# This uses the 'source' command specific to Bash shells.
source venv/bin/activate

# 2. Install Dependencies from requirements.txt
# This ensures all necessary packages are present in the environment.
pip install -r requirements.txt

# 3. Set the FLASK_APP environment variable (Good practice for Flask)
# This tells Flask where to find your application instance (e.g., 'app.py').
export FLASK_APP=app.py

# 4. Start the Flask Application
# The '--debug' flag enables the auto-reloader and debugger for development.
flask run --debug