from bson import ObjectId

from bindings import database
from business_methods.Resume import *
from business_methods.Job import *
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

def set_following_data(x, requester_id):
    x['following'] = get_following_data(x)
    x['followers'] = get_followers_data(x)

    if requester_id and requester_id != '0':
        requester = database['users'].find_one({'_id': ObjectId(requester_id)}, {'_id': 1, 'following': 1})

        if requester is None or x == dict(requester):
            return x

        requester = clean_id(requester)

        if requester["id"] in [f['id'] for f in x["followers"]] and requester["id"] in [f['id'] for f in
                                                                                        x["following"]]:
            x["badges"].append({"category": "social", "name": "You mutually follow each other"})

        elif requester["id"] in [f['id'] for f in x["followers"]]:
            x["badges"].append({"category": "social", "name": "You are a follower"})

        elif requester["id"] in [f['id'] for f in x["following"]]:
            x["badges"].append({"category": "social", "name": "Follows you"})

    return x

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
    x["badges"] = []
    x = set_following_data(x, requester_id)

    #Setting badges
    watchout_score = 100 * user_to_company_requirements(x['id'], requester_id)
    if watchout_score > 10:
        x["badges"].append({"category": "user_match", "name": "Watchout", "value": round(watchout_score, 0)})

    wanted_score = 100 * user_to_company_constraints(x['id'], requester_id)
    if wanted_score > 10:
        x["badges"].append({"category": "user_match", "name": "Wanted", "value": round(wanted_score, 0)})

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
def user_to_offer_requirements(user, job):
    res_a, res_b = resume_to_vector(user), offer_requirements_to_vector(job)
    comparison = {}
    comparison['academic'] = academic_compare(res_a, res_b)
    comparison['experience'] = experience_compare(res_a, res_b)
    comparison['lang'] = lang_compare(res_a, res_b)
    comparison['skills'] = skills_compare(res_a, res_b)
    return 1 - np.mean(list(comparison.values()))

def user_to_offer_constraints(user_id, offer_id):
    user_demands = [offer_to_demand(offer_id, str(x['_id'])) for x in database['posts'].find({'ownerId': user_id, 'type':'Demand'}, {'_id': 1})]
    return np.mean(user_demands)

def user_to_company_requirements(user_id, company_id):
    match_scores = [User.user_to_offer_requirements(user_id, str(x['_id'])) for x in database['posts'].find({'ownerId': company_id, 'type':'Offer'})]
    if len(match_scores) == 0:
        return 0
    return max(match_scores)

def user_to_company_constraints(user_id, company_id):
    match_scores = [User.user_to_offer_constraints(user_id, str(x['_id'])) for x in database['posts'].find({'ownerId': company_id, 'type':'Offer'})]
    if len(match_scores) == 0:
        return 0
    return max(match_scores)