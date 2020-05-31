from datetime import datetime

from bson import ObjectId
from business_objects.User import get_data as ugd
from bindings import database
from main import app
from url_bindings.sockets import *

quizz_namespace = '/questions/'

def get_data(query, requester_id=None, return_unique=False):
    questions = database['questions'].find(query)
    questions = [x for x in questions]
    for x in questions:
        x['id'] = str(x['_id'])
        del x['_id']


    if return_unique is False:
        return {'body': questions}
    if len(questions) == 1:
        return questions[0]
    return {'body': questions}

@app.route(quizz_namespace, methods=['GET', 'POST', 'PUT'])
def question_cru():
    if request.method == 'GET':
        return get_data({}, return_unique=False)
    elif request.method == 'POST':
        question = request.get_json()
        question['creation_date'] = str(datetime.now())
        database['questions'].insert_one(question)
        question['id'] = str(question['_id'])
        del question['_id']
        return question
    elif request.method == 'PUT':
        question = request.get_json()
        print(question, '\n')
        old_question = database['questions'].find({'_id': ObjectId(question['id'])})
        old_question = [x for x in old_question][0]
        print(old_question, '\n')
        for k, v in question.items():
            if k not in ['id', 'creation_date', 'asker']:
                old_question[k] = v

        print(old_question, '\n')
        database['questions'].update({'_id': ObjectId(question['id'])}, old_question)

        old_question['id'] = str(old_question['_id'])
        del old_question['_id']

        return old_question

@app.route(quizz_namespace + '<id>', methods=['DELETE'])
def delete_quizz(id):
    old_company = get_data({'_id': ObjectId(id)})
    database['questions'].delete_one({'_id': ObjectId(id)})
    return old_company