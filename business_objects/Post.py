from bindings import database
from business_objects import User, Company

def decrypt_password(crypted):
    return crypted

def get_data(query, requester_id=None, return_unique=False):
    def clean_id(entry):
        entry['id'] = str(entry['_id'])
        del entry['_id']
        return entry

    posts = database['posts'].find(query, {'id': 0})
    posts = [x for x in posts]
    posts = [clean_id(x) for x in posts]
    for x in posts:
        #Getting post owner data
        owner = User.get_data({'email': x['ownerId']})
        if 'body' in owner.keys() and len(owner['body']) == 0:
            owner = Company.get_data({'id': x['ownerId']})

        x['owner'] = owner
        #Setting badges
        x["badges"] = []
        if str(x['type']).endswith('offer'):
            x["badges"].append({"category": "posttype", "name": "offer"})
        elif str(x['type']).endswith('demand'):
            x["badges"].append({"category": "posttype", "name": "demand"})

        if True:
            x["badges"].append({"category": "fav", "name": "Favorite"})
        if True:
            x["badges"].append({"category": "jobtype", "name": "Stage"})
        if True:
            x["badges"].append({"category": "match", "name": "Watchout"})


    if len(posts) == 1 or return_unique:
        return posts[0]
    return {'body': posts}

class Post:
    def __init__(self):
        pass
