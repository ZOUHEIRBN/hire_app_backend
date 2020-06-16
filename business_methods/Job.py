# # Evaluating a job offer
from scipy import spatial
from business_methods import User
from bindings import database
from bson import ObjectId

import numpy as np


from business_methods.Resume_getters import *


def job_academic_to_vector(job):
    j_dict = dict((x, 0) for x in get_all_academic())
    if 'requiredDegrees' in job.keys():
        j_ac = dict((x['option'], x['level']) for x in job['requiredDegrees'])
        j_dict.update(j_ac)
    return np.array(list(j_dict.values()))


def job_experience_to_vector(job):
    j_dict = dict((x, 0) for x in get_all_experiences())
    if 'requiredExp' in job.keys():
        j_xp = dict((x['title'], x['level']) for x in job['requiredExp'])
        j_dict.update(j_xp)
    return np.array(list(j_dict.values()))


def job_lang_to_vector(job):
    j_dict = dict((x, 0) for x in get_all_languages())
    if 'requiredLanguages' in job.keys():
        j_lang = dict((x['lang'], x['level']) for x in job['requiredLanguages'])
        j_dict.update(j_lang)
    return np.array(list(j_dict.values()))


def job_skills_to_vector(job):
    j_dict = dict((x, 0) for x in get_all_skills())
    if 'requiredSkills' in job.keys():
        j_skills = dict((x['skill'], x['level']) for x in job['requiredSkills'])
        j_dict.update(j_skills)
    return np.array(list(j_dict.values()))

def offer_requirements_to_vector(post_id):
    v = {}
    job = dict(database['posts'].find_one({'_id': ObjectId(post_id)}))
    v['academic'] = job_academic_to_vector(job)
    v['experience'] = job_experience_to_vector(job)
    v['lang'] = job_lang_to_vector(job)
    v['skills'] = job_skills_to_vector(job)
    return v


def offer_constraints_to_vector(post_id):
    #     Defining contants
    sal_ranges = [0, 3000, 5000, 7000, 9000, 999999999]
    contractTypes = {'CDD': 1,
                     'CDI': 2,
                     'Stage': 3,
                     'Alternance': 4,
                     'Intérim': 5,
                     'Freelance': 6,
                     'Temps partiel': 7
                     }
    business_travels = {'None': 0, 'Rarely': 1, 'Frequently': 2}

    # Fetching user
    _off = dict(database['posts'].find_one({'_id': ObjectId(post_id)}))
    offer = {}


    if 'regular_workhours' in _off.keys():
        offer['workhours'] = _off['regular_workhours']
    else:
        offer['workhours'] = 0

    if 'additional_workhours' in _off.keys():
        offer['add_workhours'] = _off['additional_workhours']
    else:
        offer['add_workhours'] = 0

    offer['workdays'] = []
    for x in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        if x in _off['workdays']:
            offer['workdays'].append(1)
        else:
            offer['workdays'].append(0)

    if 'salary' in _off.keys():
        offer['salary'] = float(_off['salary'])
    else:
        offer['salary'] = 0

    if 'contractType' in _off.keys():
        offer['contractType'] = contractTypes[_off['contractType']]
    else:
        offer['contractType'] = 0

    if 'businessTravels_national' in _off.keys():
        offer['businessTravels_national'] = business_travels[_off['businessTravels_national']]
    else:
        offer['businessTravels_national'] = 0

    if 'businessTravels_international' in _off.keys():
        offer['businessTravels_international'] = business_travels[_off['businessTravels_international']]
    else:
        offer['businessTravels_international'] = 0
    return offer

def demand_to_vector(post_id):
    #     Defining contants
    sal_ranges = [0, 3000, 5000, 7000, 9000, 999999999]
    contractTypes = {'CDD': 1, 'CDI': 2, 'Stage': 3, 'Alternance': 4, 'Intérim': 5, 'Freelance': 6}
    business_travels = {'None': 0, 'Rarely': 1, 'Frequently': 2}

    # Fetching user
    user_demand = dict(database['posts'].find_one({'_id': ObjectId(post_id)}))
    demand = {}
    demand['workhours'] = [user_demand['min_workhours'], user_demand['max_workhours']]
    demand['workdays'] = []
    for x in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        if x in user_demand['workdays']:
            demand['workdays'].append(1)
        else:
            demand['workdays'].append(0)

    demand['salary_range'] = [float(sal_ranges[user_demand['salary_range']]),
                              float(sal_ranges[1 + user_demand['salary_range']])]
    demand['contractType'] = contractTypes[user_demand['contractType']]
    if 'businessTravels_national' in user_demand.keys():
        demand['businessTravels_national'] = business_travels[user_demand['businessTravels_national']]
    else:
        demand['businessTravels_national'] = 0

    if 'businessTravels_international' in user_demand.keys():
        demand['businessTravels_international'] = business_travels[user_demand['businessTravels_international']]
    else:
        demand['businessTravels_international'] = 0
    return demand

def offer_to_demand(offer_id, demand_id):
    demand = demand_to_vector(demand_id)
    offer = offer_constraints_to_vector(offer_id)
    match_dict = {}
    match_dict['workhours'] = (demand['workhours'][1] - offer['workhours']) / (
                demand['workhours'][1] - demand['workhours'][0])
    match_dict['workdays'] = 1 - spatial.distance.cosine(demand['workdays'], offer['workdays'])

    match_dict['salary'] = (offer['salary'] - demand['salary_range'][0]) / (
                demand['salary_range'][1] - demand['salary_range'][0])
    match_dict['contractType'] = 1 if demand['contractType'] == offer['contractType'] else 0
    match_dict['businessTravels_national'] = 1 if demand['businessTravels_national'] == offer[
        'businessTravels_national'] else 0
    match_dict['businessTravels_international'] = 1 if demand['businessTravels_international'] == offer[
        'businessTravels_international'] else 0

    return np.mean(list(match_dict.values()))

def demand_to_company_requirements(demand_id, company_id):
    offers = [User.offer_to_demand(str(x['_id']), demand_id) for x in database['posts'].find({'type': 'Offer', 'ownerId': company_id})]
    # print(offers)
    return max(offers)