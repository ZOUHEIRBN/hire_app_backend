# # Evaluating a job offer

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

def job_to_vector(post_id):
    v = {}
    job = dict(database['posts'].find_one({'_id': ObjectId(post_id)}))
    v['academic'] = job_academic_to_vector(job)
    v['experience'] = job_experience_to_vector(job)
    v['lang'] = job_lang_to_vector(job)
    v['skills'] = job_skills_to_vector(job)
    return v