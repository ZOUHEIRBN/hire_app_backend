import pandas as pd

from flask import Response, request, render_template, send_file
import requests
from business_objects.User import *
from bindings import database, client, SERVER_URL
from main import app
from url_bindings.users import user_namespace

from weasyprint import HTML, CSS
from io import BytesIO

@app.route(user_namespace+'<id>/resume/', methods=['GET', 'PUT', 'DELETE'])
def crud_resume(id):
    if request.method == 'PUT':
        resume = request.get_json()
        database['users'].update({'_id': ObjectId(id)}, {"$set": {"resume": resume}})
        return resume

    elif request.method == 'DELETE':
        resume = {
          "academic_cursus": [],
          "professionnal_cursus": [],
          "academic_projects": [],
          "languages": [],
          "skills": [],
        }
        database['users'].update({'_id': ObjectId(id)}, {"$set": {"resume": resume}})
        return resume

    elif request.method == 'GET':
        resume = get_data({'_id': ObjectId(id)})['resume']
        return {'body': resume}

    return {}

@app.route(user_namespace+'<id>/resume/write', methods=['GET'])
def write_resume(id):
    resume_user = get_data({'_id': ObjectId(id)})
    return render_template('resume_template.html', user=resume_user)

@app.route(user_namespace+'<id>/resume/pdf', methods=['GET'])
def get_pdf_resume(id):
    #html = HTML(SERVER_URL+user_namespace+id+'/resume/write')
    r = requests.get(SERVER_URL+user_namespace+id+'/resume/write').content
    print(r)
    html = HTML(string=r)
    pdf = html.write_pdf()
    return send_file(BytesIO(pdf), attachment_filename='google.pdf')


#Backend only methods
def get_competency_mat(query={}):
    competency_mat = database['users'].find(query, {'resume.skills': 1, 'resume.languages': 1})
    list = []
    for x in competency_mat:
        skills = x['resume']['skills']
        lang = x['resume']['languages']
        skill_dict = {'profile_id': str(x['_id'])}
        for l in lang:
            skill_dict.update({l['lang']: l['level']})

        for s in skills:
            skill_dict.update({s['skill']: s['level']})

        list.append(skill_dict)

    df = pd.DataFrame(list)
    df = df[sorted(df.columns.tolist())]
    df = df.fillna(int(0))
    values = df.values
    return dict((v[-1], [n for n in v[:-1]]) for v in values), df.columns.tolist()

def to_vector(id):
    return get_competency_mat({'_id': ObjectId(id)})[0]