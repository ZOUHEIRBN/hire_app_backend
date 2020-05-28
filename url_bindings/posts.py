import time, datetime
from bson import ObjectId
from flask import request
from bindings import database
from business_objects.Post import get_data, preprocess
from business_objects.User import get_data as ugd
from main import app, socket

post_namespace = '/posts/'


@app.route(post_namespace, methods=['GET', 'POST', 'PUT'])
def post_crd():
    if request.method == 'GET':
        return get_data({})
    elif request.method == 'POST':
        post = request.get_json()
        post['submissions'] = []
        post['comments'] = []
        database['posts'].insert_one(post)
    elif request.method == 'PUT':
        post = request.get_json()
        old_post = get_data({'_id': ObjectId(post['id'])})
        for k, v in post.items():
            if k not in ['id','comments', 'ownerId']:
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
        database['posts'].update({'_id': ObjectId(post_id)}, {
         '$push': {'comments': comment}
        })
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