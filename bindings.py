from flask_socketio import SocketIO, send
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import time

#Loading Database
client = MongoClient(port=27017)
database = client["HireApp"]

ts = time.time()
print('Application backend launched at: {:.0f}'.format(ts*1000))

SERVER_URL = 'http://localhost:3000'
app = Flask(__name__, template_folder='./templates', static_folder='./static')
CORS(app)
socket = SocketIO(app, cors_allowed_origins="*")

from url_bindings import users, posts, company, resume, sockets