from datetime import datetime

from bson import ObjectId

from bindings import database
from business_objects.Company import get_data, preprocess
from main import app
from url_bindings.sockets import *

company_namespace = '/companies/'


@app.route(company_namespace, methods=['GET', 'POST'])
def company_cr():
    if request.method == 'GET':
        return get_data({}, requester_id=request.args.get('current_user'), return_unique=False)
    elif request.method == 'POST':
        company = request.get_json()
        database['companies'].insert_one(company)
    return {}


@app.route(company_namespace+'<id>')
def get_company(id, requester_id=None):
    try:
        return get_data({'_id': ObjectId(id)}, requester_id)
    except:
        return get_data({'email': id}, requester_id)


@app.route(company_namespace+'ownerId/<id>')
def get_companies_by_owner_id(id):
    return get_data({'ownerId': id})


@app.route(company_namespace+'type/<type>')
def get_companies_by_type(type):
    return get_data({'type': type})

@app.route(company_namespace+'<following_id>/follow', methods=['PUT'])
def follow_company(following_id):
    current = request.get_json()
    if current is None:
        current = get_company(following_id)
        return current

    f_list = database['users'].find({'_id': ObjectId(current['id'])}, {'_id':0, 'following': 1})
    f_list = [f for f in f_list][0]['following']

    if {'id': ObjectId(following_id)} in f_list: #Unfollow
        database['users'].update({'_id': ObjectId(current['id'])}, {
            '$pull': {'following': {'id': ObjectId(following_id)}}
        })
        unfollowed = get_company(following_id, current['id'])
        return unfollowed

    else: #Follow
        database['users'].update({'_id': ObjectId(current['id'])}, {
            '$push': {'following': {'id': ObjectId(following_id)}}
        })

        #Notify the user of new follower
        new_followed = get_data({'_id': ObjectId(following_id)}, requester_id=current['id'])
        notification = {
            'id': str(ObjectId()),
            'from': current,
            'title': '{} {} (@{}) has started following your company {}'.format(current['first_name'], current['last_name'].upper(), current['email'], new_followed['title']),
            'timestamp': str(datetime.now()),
            'state': True,
            'type': 'Users',
            'imageUrl': current['imageUrl']
        }
        recipients = [k for k, v in sids.items() if v == new_followed['ownerId']]
        for r in recipients:
            notify(r, notification, 'user_following')

        return new_followed



