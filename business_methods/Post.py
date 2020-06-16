from bindings import database
from business_methods import User, Job, Company
from bson import ObjectId
from utility_functions import *


def decrypt_password(crypted):
    return crypted


def get_owner_data(x):
    owner = User.get_data({'_id': ObjectId(x['ownerId'])})
    if 'body' in owner.keys() and len(owner['body']) == 0:
        owner = Company.get_data({'_id': ObjectId(x['ownerId'])})

    x['owner'] = owner
    return x


def get_comment_data(x):
    for comment in x['comments']:
        comment['id'] = str(comment['id'])
        print(comment['commenting_user'])
        commenting_user = User.get_data({
            '_id': ObjectId(comment['commenting_user'])
        })

        if 'body' in commenting_user.keys() and len(commenting_user['body']) == 0:
            commenting_user = Company.get_data({
                '_id': ObjectId(comment['commenting_user'])
            })

        comment['commenting_user'] = commenting_user

    return x


def check_following(x, requester_id):
    x['following'] = False
    submissions = dict(database['posts'].find_one({'_id': ObjectId(x['id'])}, {"follows": 1}))
    if "follows" in submissions.keys():
        if requester_id in submissions["follows"]:
            x['following'] = True

    return x

def set_offer_badges(x, requester_id):
    x["badges"] = []
    x["badges"].append({"category": "posttype", "name": "Offer"})
    if requester_id is not None and str(requester_id) != '0':
        # Set Watchout badge
        watchout_score = [u['score'] for u in x['watchout'] if u['id'] == requester_id]
        watchout_score = 100 * watchout_score[0] if len(watchout_score) > 0 else 0
        if watchout_score > 1:
            x["badges"].append({"category": "offer_match", "name": "Watchout", "value": round(watchout_score, 0)})

        # Set Wanted badge
        wanted_score = 100 #* User.user_to_offer_constraints(requester_id, x['id'])
        if wanted_score > 1:
            x["badges"].append({"category": "offer_match", "name": "Wanted", "value": round(wanted_score, 0)})

    return x

def set_demand_badges(x, requester_id):
    x["badges"] = []
    x["badges"].append({"category": "posttype", "name": "Demand"})
    maxwatchout = 100*Job.demand_to_company_requirements(x['id'], x['ownerId'])
    if maxwatchout > 10:
        x["badges"].append({"category": "demand_match", "name": "Wanted", "value": round(maxwatchout, 0)})
    return x

def preprocess(x, requester_id=None):
    # Rename _id to id
    x['id'] = str(x['_id'])
    del x['_id']

    # Getting post owner data
    x = get_owner_data(x)

    # Getting commenting users data
    x = get_comment_data(x)

    # Checking following
    x = check_following(x, requester_id)

    # Setting badges
    if str(x['type']).lower().endswith('offer'):
        x = set_offer_badges(x, requester_id)
    elif str(x['type']).lower().endswith('demand'):
        x = set_demand_badges(x, requester_id)

    # Setting an image if not provided
    if 'imageUrl' not in x.keys():
        x['imageUrl'] = 'data:image/png;base64, ' + generate_profile_image().decode('utf-8')
    return x


def get_data(query, requester_id=None, return_unique=False):
    posts = database['posts'].find(query, {'id': 0})
    posts = [x for x in posts]
    posts = [preprocess(x, requester_id) for x in posts]

    if len(posts) == 1 or return_unique:
        return posts[0]
    return {'body': posts}


def set_user_watchouts(job_id):
    users = [str(x['_id']) for x in database['users'].find({}, {'_id': 1, 'email': 1})]
    wa_scores = [{'id': x, 'score': User.user_to_offer_requirements(x, job_id)} for x in users]
    database['posts'].update_one({'_id': ObjectId(job_id)}, {'$set': {'watchout': wa_scores}})
    return wa_scores
