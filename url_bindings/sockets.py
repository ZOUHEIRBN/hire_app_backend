from bindings import socket
from flask_socketio import send
from flask import request


def notify(client_id, data):
    socket.emit('notification', data, room=client_id)
    #print('Notifying client "{}" \nBody: "{}".'.format(client_id, data))

@socket.on('new_connection')
def new_connection(notification):
    notify(request.sid, {'body': notification})