from bson import ObjectId

from bindings import database
from utility_functions import *


def decrypt_password(crypted):
    return crypted
def get_following_data(x):
    following = database['users'].find({
        '_id': {'$in': [f['id'] for f in x['following']]}
    },
        {'_id': 1, 'email': 1, 'first_name': 1, 'last_name': 1, 'imageUrl': 1})
    following = [f for f in following]
    following = [clean_id(f) for f in following]
    return following

def get_followers_data(x):
    followers = database['users'].find({
        'following': {'$elemMatch': {'$eq': {'id': ObjectId(x['id'])}
                                     }}
    },
        {'_id': 1, 'email': 1, 'first_name': 1, 'last_name': 1, 'imageUrl': 1})
    followers = [f for f in followers]
    followers = [clean_id(f) for f in followers]
    return followers

def clean_id(x):
    if '_id' in x.keys():
        x['id'] = str(x['_id'])
        del x['_id']

    elif x['id'] is not None:
        x['id'] = str(x['id'])

    return x

def preprocess(x, requester_id=None):
    x = clean_id(x)
    # Follower data
    x['following'] = get_following_data(x)
    x['followers'] = get_followers_data(x)
    x["badges"] = []
    if requester_id and requester_id != '0':
        requester = database['users'].find_one({'_id': ObjectId(requester_id)}, {'_id': 1, 'following': 1})

        if requester is None or x == dict(requester):
            return x

        requester = clean_id(requester)

        if requester["id"] in [f['id'] for f in x["followers"]] and requester["id"] in [f['id'] for f in x["following"]]:
            x["badges"].append({"category": "social", "name": "You mutually follow each other"})

        elif requester["id"] in [f['id'] for f in x["followers"]]:
            x["badges"].append({"category": "social", "name": "You are a follower"})

        elif requester["id"] in [f['id'] for f in x["following"]]:
            x["badges"].append({"category": "social", "name": "Follows you"})
    if True:
        x["badges"].append({"category": "match", "name": "Watchout"})

    # Setting an image if not provided
    if 'imageUrl' not in x.keys():
        x['imageUrl'] = 'data:image/png;base64, ' + generate_profile_image().decode('utf-8')
    return x

def get_data(query, requester_id=None, return_unique=False):


    users = database['users'].find(query, {'password': 0})
    users = [x for x in users]
    users = [preprocess(x, requester_id) for x in users]

    if len(users) == 1 or return_unique:
        return users[0]
    return {'body': users}

class User:
    def __init__(self):
        pass
