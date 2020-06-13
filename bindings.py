from flask_socketio import SocketIO, send
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import time
from celery import Celery


def make_celery(app_object):
    celery = Celery(
        app_object.import_name,
        backend=app_object.config['CELERY_RESULT_BACKEND'],
        broker=app_object.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app_object.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app_object.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

#Loading Database
client = MongoClient(port=27017)
database = client["HireApp"]

ts = time.time()
print('Application backend launched at: {:.0f}'.format(ts*1000))

SERVER_URL = 'http://localhost:3000'
app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
CORS(app)
socket = SocketIO(app, cors_allowed_origins="*")
celery = make_celery(app)

from url_bindings import users, posts, company, resume, sockets, questions