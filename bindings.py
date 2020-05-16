from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import time

#Loading Database
client = MongoClient(port=27017)
database = client["HireApp"]

ts = time.time()
print('Application backend launched at: {:.0f}'.format(ts*1000))
app = Flask(__name__)
CORS(app)

from url_bindings import users, posts, company