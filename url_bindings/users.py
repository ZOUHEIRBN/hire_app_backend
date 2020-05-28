from datetime import datetime

from bson import ObjectId
from flask import Response, request

from business_objects.User import *
from bindings import database, client
from url_bindings.sockets import *
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

@app.route(user_namespace+'<following_id>/follow', methods=['PUT'])
def follow(following_id):
    current = request.get_json()
    f_list = database['users'].find({'_id': ObjectId(current['id'])}, {'_id':0, 'following': 1})
    f_list = [f for f in f_list][0]['following']

    if current is None:
        return {}

    if {'id': ObjectId(following_id)} in f_list: #Unfollow
        database['users'].update({'_id': ObjectId(current['id'])}, {
            '$pull': {'following': {'id': ObjectId(following_id)}}
        })

    else: #Follow
        database['users'].update({'_id': ObjectId(current['id'])}, {
            '$push': {'following': {'id': ObjectId(following_id)}}
        })

        #Notify the user of new follower
        new_followed = get_user(following_id)
        notification = {
            'id': str(ObjectId()),
            'from': current,
            'title': '{} {} ({}) has started following you'.format(current['first_name'], current['last_name'].upper(), current['email']),
            'timestamp': str(datetime.now()),
            'state': True,
            'type': 'Users',
            'imageUrl': current['imageUrl']
        }
        recipients = [k for k, v in sids.items() if v == new_followed['email']]
        print(sids)
        for r in recipients:
            notify(r, notification, 'user_following')

    return current

