from flask import request
from bindings import database
from main import app

company_namespace = '/companies/'


@app.route(company_namespace, methods=['GET', 'POST'])
def company_cr():
    if request.method == 'GET':
        companies = database['companies'].find({}, {'_id': 0})
        companies = [x for x in companies]
        return {'body': companies}
    elif request.method == 'POST':
        company = request.get_json()
        database['companies'].insert_one(company)
    return {}


@app.route(company_namespace+'<id>')
def get_company(id):
    company = database['companies'].find({'id': id}, {'_id': 0})
    company = [x for x in company]
    try:
        return company[0]
    except:
        return {}


@app.route(company_namespace+'ownerId/<id>')
def get_companies_by_owner_id(id):
    companies = database['companies'].find({'ownerId': id}, {'_id': 0})
    companies = [x for x in companies]
    return {'body': companies}


@app.route(company_namespace+'type/<type>')
def get_companies_by_type(type):
    companies = database['companies'].find({'type': type}, {'_id': 0})
    companies = [x for x in companies]
    return {'body': companies}

