from bson import ObjectId
from flask import Response, request

from business_objects.User import *
from bindings import database, client
from main import app

user_namespace = '/users/'

@app.route(user_namespace, methods=['GET', 'POST'])
def user_cr():
    if request.method == 'GET':
        return get_data({}, requester_id=request.args.get('current_user'))
    elif request.method == 'POST':
        user = request.get_json()
        database['users'].insert_one(user)
        #database['users'].update_many({'email': 'ZouheirBN'}, {'$push': {'following'}})
    return {}

@app.route(user_namespace+'<id>')
def get_user(id):
    return get_data({'_id': ObjectId(id)})

@app.route(user_namespace+'email/<email>')
def get_user_by_email(email):
    return get_data({'email': email})

@app.route(user_namespace+'credentials/<email>/<password>')
def get_user_by_credentials(email, password):
    password = decrypt_password(password)
    user = get_data({'email': email, 'password': password}, return_unique=True)
    if Response(user).content_length != 0:
        try:
            return user
        except:
            return {}
    return {}




