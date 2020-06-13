from bson import ObjectId

from bindings import database
from business_methods.Resume import *
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

#User similarity
def user_to_user(user_a, user_b):
    res_a, res_b = resume_to_vector(user_a), resume_to_vector(user_b)
    comparison = {}
    comparison['academic'] = academic_compare(res_a, res_b)
    comparison['experience'] = experience_compare(res_a, res_b)
    comparison['lang'] = lang_compare(res_a, res_b)
    comparison['skills'] = skills_compare(res_a, res_b)
    return 1 - np.mean(list(comparison.values()))

#Match score
def user_to_offer(user, job):
    res_a, res_b = resume_to_vector(user), job_to_vector(job)
    comparison = {}
    comparison['academic'] = academic_compare(res_a, res_b)
    comparison['experience'] = experience_compare(res_a, res_b)
    comparison['lang'] = lang_compare(res_a, res_b)
    comparison['skills'] = skills_compare(res_a, res_b)
    return 1 - np.mean(list(comparison.values()))