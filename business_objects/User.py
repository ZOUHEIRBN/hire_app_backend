from bson import ObjectId

from bindings import database


def decrypt_password(crypted):
    return crypted
def get_following_data(x):
    followers = database['users'].find({
        'email': {'$in': x['following']}
    },
        {'_id': 0, 'password': 0})
    followers = [f for f in followers]
    return followers

def get_data(query, requester_id=None, return_unique=False):
    def clean_id(entry):
        entry['id'] = str(entry['_id'])
        del entry['_id']
        return entry

    users = database['users'].find(query, {'password': 0})
    users = [x for x in users]
    users = [clean_id(x) for x in users]
    for x in users:
        # Follower data
        x['following'] = get_following_data(x)

        x["badges"] = []
        if requester_id:
            requester = database['users'].find_one({'email': requester_id}, {'_id': 0, 'password': 0})

            if requester is None or x == dict(requester):
                continue

            if requester["email"] in x["following"] and x["email"] in requester["following"]:
                x["badges"].append({"category": "social", "name": "Friend"})

            elif x["email"] in requester["following"]:
                x["badges"].append({"category": "social", "name": "Follower"})

            elif requester["email"] in x["following"]:
                x["badges"].append({"category": "social", "name": "Following"})
        if True:
            x["badges"].append({"category": "match", "name": "Watchout"})



    if len(users) == 1 or return_unique:
        return users[0]
    return {'body': users}

class User:
    def __init__(self):
        pass
