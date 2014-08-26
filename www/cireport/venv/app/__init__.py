
import ConfigParser

import flask
import pymongo
import os

MY_PATH = os.path.abspath(os.path.normpath(os.path.dirname(__file__)))
# Load configuration
config = ConfigParser.ConfigParser()
config.read(os.path.join(MY_PATH, 'app.config'))

# Flask app
app = flask.Flask(__name__)
app.secret_key = 'put secret key here'

# Connect to db
host = config.get('database', 'host')
database = config.get('database', 'database')
col = config.get('database','collection')
db = pymongo.Connection(host)[database]
collection = db[col]

# Set up routes and content
from app import views
