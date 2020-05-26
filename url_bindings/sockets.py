from bson import ObjectId

from bindings import socket
from flask_socketio import send
from flask import request
from datetime import datetime

sids = {}
def notify(client_id, data):
    #This function sends notifications to a client
    socket.emit('notification', data, room=client_id)

@socket.on('new_connection')
def new_connection(user_data):
    #When a user connects, send them a notification
    sids[user_data['email']] = request.sid
    notification = {
        'id': str(ObjectId()),
        'from': user_data['email'],
        'title': '{} has connected'.format(user_data['email']),
        'timestamp': str(datetime.now()),
        'state':True,
        'type': 'Users',
        'imageUrl': user_data['imageUrl']
    }
    recipients = [v for k, v in sids.items() if k == user_data['email'] or k in user_data['following']]
    for r in recipients:
        notify(r, notification)

