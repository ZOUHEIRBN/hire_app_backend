from bindings import database
from business_methods import User, Company
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


def preprocess(x, requester_id=None):
    # Rename _id to id
    x['id'] = str(x['_id'])
    del x['_id']

    print(x['id'])

    # Getting post owner data
    x = get_owner_data(x)

    # Getting commenting users data
    x = get_comment_data(x)

    # Checking following
    x = check_following(x, requester_id)

    # Setting badges
    x["badges"] = []

    if str(x['subject']).lower().endswith('offer'):
        x["badges"].append({"category": "posttype", "name": "offer"})
    elif str(x['subject']).lower().endswith('demand'):
        x["badges"].append({"category": "posttype", "name": "demand"})

    # if True:
    #     x["badges"].append({"category": "fav", "name": "Favorite"})
    # if True:
    #     x["badges"].append({"category": "jobtype", "name": "Stage"})
    if requester_id is not None and str(requester_id) != '0':
        watchout_score = [u['score'] for u in x['watchout'] if u['id'] == requester_id]
        watchout_score = 100*watchout_score[0] if len(watchout_score) > 0 else 0
        wanted_score = 100*User.user_to_offer_constraints(requester_id, x['id'])

        if watchout_score > 10 and wanted_score > 10 and False:
            x["badges"].append({
                "category": "match",
                "name": "Golden match",
                "value": round(watchout_score + wanted_score)//2})

        else:
            # Set Watchout badge
            if watchout_score > 1:
                x["badges"].append({"category": "match", "name": "Watchout", "value": round(watchout_score, 1)})

            # Set Wanted badge
            if wanted_score > 1:
                x["badges"].append({"category": "match", "name": "Wanted", "value": round(wanted_score, 1)})

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
