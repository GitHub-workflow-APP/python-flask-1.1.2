from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

from . import views

app.register_blueprint(views.bp)


