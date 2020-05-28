from bson import ObjectId

from bindings import database


def decrypt_password(crypted):
    return crypted
def get_following_data(x):
    following = database['users'].find({
        'email': {'$in': x['following']}
    },
        {'_id': 1, 'email': 1, 'first_name': 1, 'last_name': 1, 'imageUrl': 1})
    following = [f for f in following]
    following = [clean_id(f) for f in following]
    return following

def get_followers_data(x):
    followers = database['users'].find({
        'following': {'$elemMatch': {'$eq': x['email']}}
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
    if requester_id:
        requester = database['users'].find_one({'email': requester_id}, {'_id': 0, 'password': 0})

        if requester is None or x == dict(requester):
            return x

        if requester["email"] in x["following"] and x["email"] in requester["following"]:
            x["badges"].append({"category": "social", "name": "Friend"})

        elif x["email"] in requester["following"]:
            x["badges"].append({"category": "social", "name": "Follower"})

        elif requester["email"] in x["following"]:
            x["badges"].append({"category": "social", "name": "Following"})
    if True:
        x["badges"].append({"category": "match", "name": "Watchout"})

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
