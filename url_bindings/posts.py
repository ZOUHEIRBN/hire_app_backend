import time, datetime
from bson import ObjectId
from flask import request
from bindings import database
from business_objects.Post import get_data
from business_objects.User import get_data as ugd
from main import app, socket

post_namespace = '/posts/'


@app.route(post_namespace+'current_id=<requester_id>', methods=['GET', 'POST', 'PUT'])
def post_crd(requester_id):
    if request.method == 'GET':
        return get_data({}, requester_id=requester_id)
    elif request.method == 'POST':
        post = request.get_json()
        post['submissions'] = []
        post['comments'] = []
        post['timestamp'] = datetime.datetime.now()
        database['posts'].insert_one(post)
    elif request.method == 'PUT':
        post = request.get_json()
        old_post = get_data({'_id': ObjectId(post['id'])})
        for k, v in post.items():
            if k not in ['id', 'comments', 'timestamp', 'owner']:
                old_post[k] = v

        database['posts'].update({'_id': ObjectId(post['id'])}, old_post)

        old_post['owner'] = ugd({'_id': ObjectId(old_post['ownerId'])})

        return old_post


    return {}


@app.route(post_namespace+'<id>', methods=['GET', 'DELETE'])
def get_post(id):
    if request.method == 'GET':
        try:
            return get_data({'_id': ObjectId(id)})
        except:
            return {}
    elif request.method == 'DELETE':
        post = database['posts'].find_one({'_id': ObjectId(id)})
        post['id'] = id
        del post['_id']

        database['posts'].delete_one({'_id': ObjectId(id)})
        return post


@app.route(post_namespace+'ownerId/<id>')
def get_posts_by_owner_id(id):
    return get_data({'ownerId': id})


@app.route(post_namespace+'type/<type>')
def get_posts_by_type(type):
    return get_data({'type': type})

@app.route(post_namespace+'follow/<user_id>', methods=['PUT'])
def submit_demand(user_id):
    post = request.get_json()
    follows = dict(database['posts'].find_one({'_id': ObjectId(post['id'])}, {"follows": 1}))
    if "follows" in follows.keys():
        if user_id not in follows["follows"]:
            database['posts'].update_one({'_id': ObjectId(post['id'])}, {'$push': {'follows': user_id}})
            post['following'] = True
        else:
            database['posts'].update_one({'_id': ObjectId(post['id'])}, {'$pull': {'follows': user_id}})
            post['following'] = False

    else:
        database['posts'].update_one({'_id': ObjectId(post['id'])}, {'$set': {'follows': [user_id]}})
        post['following'] = True
    return post

#Comments
@app.route(post_namespace+'<post_id>/comment/<comment_id>', methods=['PUT', 'POST', 'DELETE'])
def comment_cud(post_id, comment_id):
    if request.method == 'POST':
        comment = request.get_json()
        comment['timestamp'] = str(datetime.datetime.now())
        comment['id'] = ObjectId.from_datetime(datetime.datetime.now())
        database['posts'].update({'_id': ObjectId(post_id)}, {
         '$push': {'comments': comment}
        })
        comment['id'] = str(comment['id'])
        comm_user = ugd({'_id': ObjectId(comment['commenting_user'])})
        comment['commenting_user'] = comm_user
        return comment
    elif request.method == 'PUT':
        comment = request.get_json()
        comment['timestamp'] = str(datetime.datetime.now())

        new_comment = comment
        new_comment['commenting_user'] = comment['commenting_user']['id']

        #Remove old comment
        database['posts'].update({'_id': ObjectId(post_id)}, {
            '$pull': {'comments': {'id': ObjectId(comment_id)}}
        })

        # Insert new comment
        database['posts'].update({'_id': ObjectId(post_id)}, {
            '$push': {'comments': new_comment}
        })
        return comment

    elif request.method == 'DELETE':
        comment = database['posts'].find({"_id": ObjectId(post_id)}, {'comments': 1})
        comment = [x['comments'] for x in comment][0]
        comment = [x for x in comment if x['id'] == ObjectId(comment_id)][0]

        comment['id'] = str(comment['id'])

        database['posts'].update({'_id': ObjectId(post_id)}, {
        '$pull': {'comments': {'id': ObjectId(comment_id)}}
        })

        return comment

    return {}