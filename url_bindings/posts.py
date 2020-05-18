import time, datetime
from bson import ObjectId
from flask import request
from bindings import database
from business_objects.Post import get_data
from main import app

post_namespace = '/posts/'


@app.route(post_namespace, methods=['GET', 'POST'])
def post_cr():
    if request.method == 'GET':
        return get_data({})
    elif request.method == 'POST':
        post = request.get_json()
        database['posts'].insert_one(post)
    return {}


@app.route(post_namespace+'<id>')
def get_post(id):
    try:
        return get_data({'_id': ObjectId(id)})
    except:
        return {}


@app.route(post_namespace+'ownerId/<id>')
def get_posts_by_owner_id(id):
    return get_data({'ownerId': id})


@app.route(post_namespace+'type/<type>')
def get_posts_by_type(type):
    return get_data({'type': type})

#Comments
@app.route(post_namespace+'<post_id>/comment/', methods=['PUT', 'POST'])
def add_comment(post_id):
    if request.method == 'POST':
        comment = request.get_json()
        comment['timestamp'] = str(datetime.datetime.now())
        print(comment)
        database['posts'].update({'_id': ObjectId(post_id)}, {
         '$push': {'comments': comment}
        })
    elif request.method == 'PUT':
        comment = request.get_json()
        comment['timestamp'] = str(datetime.datetime.now())
        print(comment)
        database['posts'].update({'_id': ObjectId(post_id)}, {
         '$push': {'comments': comment}
        })
    return {}