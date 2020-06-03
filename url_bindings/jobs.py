from bson import ObjectId
from bindings import database
from url_bindings import resume, posts
from math import *
import pandas as pd


def match_score(user_skill_level, required_skill_level):
    v = pi*(user_skill_level - required_skill_level)/18
    return round(tanh(v), 3)


def match_user_by_skills(job_id, user_id):
    job = database['posts'].find({'_id': ObjectId(job_id)}, {'requiredSkills': 1})
    user = database['users'].find({'_id': ObjectId(user_id)}, {'resume.skills': 1})

    job_skills = [x for x in job][0]
    if 'requiredSkills' in job_skills.keys():
        job_skills = job_skills['requiredSkills']
    else:
        return 0


    user_skills = [x for x in user][0]
    if 'resume' in user_skills.keys() and 'skills' in user_skills['resume'].keys():
        user_skills = user_skills['resume']['skills']
    else:
        return 0

    us = []

    for js in job_skills:
        for skill in user_skills:
            if skill['skill'] == js['skill']:
                us.extend([{'skill': skill['skill'], 'score': skill['level'] - js['level']}])

    final = sum([x['score'] for x in us])
    final = 1/(1+exp(-final))
    return final

def match_user_by_constraints(job_id, user_id):
    job = database['posts'].find({'_id': ObjectId(job_id)}, {'requiredSkills': 1})
    user = database['users'].find({'_id': ObjectId(user_id)}, {'resume.skills': 1})

    job_skills = [x for x in job][0]
    if 'requiredSkills' in job_skills.keys():
        job_skills = job_skills['requiredSkills']
    else:
        return 0

    user_skills = [x for x in user][0]
    if 'resume' in user_skills.keys() and 'skills' in user_skills['resume'].keys():
        user_skills = user_skills['resume']['skills']
    else:
        return 0

    us = []

    for js in job_skills:
        for skill in user_skills:
            if skill['skill'] == js['skill']:
                us.extend([{'skill': skill['skill'], 'score': skill['level'] - js['level']}])

    final = sum([x['score'] for x in us])
    final = 1/(1+exp(-final))
    return final


def to_vector(job_id):
    job = database['posts'].find({'_id': ObjectId(job_id)}, {'requiredLanguages': 1, 'requiredSkills': 1})
    job = [x for x in job]
    list = []
    for x in job:
        skills = x['requiredSkills']
        lang = x['requiredLanguages']
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
    return dict((v[-1], [n for n in v[:-1]]) for v in values), df.columns.tolist()[:-1]


def match_user_skills(job_id, user_id):
    user_vec = resume.to_vector(user_id)[user_id]
    job_vec = to_vector(job_id)[0][job_id]

    print(user_vec, job_vec)


# watchout = match_user_by_skills('5e92f8b03bc187865692b516', '5e92f8b03bc187865692b517')
# print(watchout)