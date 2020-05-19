from bindings import database
from business_objects import User, Company
from bson import ObjectId
def decrypt_password(crypted):
    return crypted

def preprocess(x):
    #Rename _id to id
    x['id'] = str(x['_id'])
    del x['_id']

    # Getting post owner data
    owner = User.get_data({'email': x['ownerId']})
    if 'body' in owner.keys() and len(owner['body']) == 0:
        owner = Company.get_data({'id': x['ownerId']})

    x['owner'] = owner

    # Getting commenting users data
    for comment in x['comments']:
        commenting_user = User.get_data({
            '_id': ObjectId(comment['commenting_user'])
        })

        if 'body' in commenting_user.keys() and len(commenting_user['body']) == 0:
            commenting_user = Company.get_data({
                '_id': ObjectId(comment['commenting_user'])
            })

        comment['commenting_user'] = commenting_user

    # Setting badges
    x["badges"] = []

    if str(x['subject']).lower().endswith('offer'):
        x["badges"].append({"category": "posttype", "name": "offer"})
    elif str(x['subject']).lower().endswith('demand'):
        x["badges"].append({"category": "posttype", "name": "demand"})

    if True:
        x["badges"].append({"category": "fav", "name": "Favorite"})
    if True:
        x["badges"].append({"category": "jobtype", "name": "Stage"})
    if True:
        x["badges"].append({"category": "match", "name": "Watchout", "value": 89})

    return x

def get_data(query, requester_id=None, return_unique=False):
    posts = database['posts'].find(query, {'id': 0})
    posts = [x for x in posts]
    posts = [preprocess(x) for x in posts]

    if len(posts) == 1 or return_unique:
        return posts[0]
    return {'body': posts}

class Post:
    def __init__(self):
        pass
