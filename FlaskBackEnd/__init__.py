"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages, sessions

import FlaskBackEnd.views
