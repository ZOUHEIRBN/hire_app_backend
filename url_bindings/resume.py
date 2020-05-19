from bson import ObjectId
from flask import Response, request, render_template, send_file

from business_objects.User import *
from bindings import database, client, SERVER_URL
from main import app
from url_bindings.users import user_namespace

from weasyprint import HTML, CSS
from io import BytesIO

@app.route(user_namespace+'<id>/resume/', methods=['GET', 'PUT'])
def crud_resume(id):
    if request.method == 'PUT':
        resume = request.get_json()
        database['users'].update({'_id': ObjectId(id)}, {"$set": {"resume": resume}})

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
    html = HTML(SERVER_URL+user_namespace+id+'/resume/write')
    pdf = html.write_pdf()
    return send_file(BytesIO(pdf), attachment_filename='google.pdf')

