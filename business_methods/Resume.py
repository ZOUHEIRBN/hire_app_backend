import time, datetime
from scipy import spatial

from business_methods.Job import *


# # Evaluating user by his resume

# To have an idea about user's ability to excel at the post, we need to evaluate his CV by parsing their skills, languages, academic and professional experiences to vectors and comparing them to the offer in question

def academic_to_vector(resume):
    def evaluate_bac_plus(x):
        if x['degree'] == 'PHD':
            return 7
        elif x['degree'] in ['MBA', 'Master', 'Engineer']:
            return 5
        elif x['degree'] in ['Bachelor', 'Technicien Spécialisé']:
            return 3
        elif x['degree'] in ['DEUG', 'Technicien']:
            return 2
            
        return 0
        
    _ac = dict((x, 0) for x in get_all_academic())
    u_ac = dict((x['title'], evaluate_bac_plus(x)) for x in resume['academic_cursus'])
    _ac.update(u_ac)
    return np.array(list(_ac.values()))


def experience_to_vector(resume):
    def calculate_exp_duration(x): 
        begin_date = datetime.datetime.strptime(x['begin_date'],"%Y-%m-%dT%X.%fZ").timetuple()
        end_date = datetime.datetime.strptime(x['end_date'],"%Y-%m-%dT%X.%fZ").timetuple()

        xp_years = (end_date.tm_year - begin_date.tm_year) + (end_date.tm_mon - begin_date.tm_mon)/12

        return round(xp_years, 1)
    
    _xp = dict((x, 0) for x in get_all_experiences())
    u_xp = dict((x['title'], calculate_exp_duration(x)) for x in resume['professionnal_cursus'])
    _xp.update(u_xp)
    return np.array(list(_xp.values()))


def lang_to_vector(resume):
    _lang = dict((x, 0) for x in get_all_languages())
    u_lang = dict((x['lang'], x['level']) for x in resume['languages'])
    _lang.update(u_lang)
    return np.array(list(_lang.values()))


def skills_to_vector(resume):
    _skill = dict((x, 0) for x in get_all_skills())
    u_skill = dict((x['skill'], x['level']) for x in resume['skills'])
    _skill.update(u_skill)
    return np.array(list(_skill.values()))


# Building comparison dictionnaries

# Dict data structures containing vectors for academic, experience, skills and languages converted to vectors
# Applicable to JobOffer and Resume obejct types

def resume_to_vector(user_id):
    v = {}
    resume = dict(database['users'].find_one({'_id': ObjectId(user_id)}))
    if 'resume' not in resume.keys():
        return v
    resume = resume['resume']
    v['academic'] = academic_to_vector(resume)
    v['experience'] = experience_to_vector(resume)
    v['lang'] = lang_to_vector(resume)
    v['skills'] = skills_to_vector(resume)
    return v



# Comparators

def academic_compare(res_a, res_b):
    if len(res_a['academic']) != len(res_b['academic']):
        raise('Unequal vectors exception')
    
    i = 0
    a  = list(res_a['academic'])
    b  = list(res_b['academic'])
    while i < len(a):
        if a[i] == 0 and b[i] == 0:
            a.pop(i)
            b.pop(i)
        i = i + 1
    
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 1.
        
    value = spatial.distance.cosine(a, b)
    return value


def experience_compare(res_a, res_b):
    if len(res_a['experience']) != len(res_b['experience']):
        raise('Unequal vectors exception')
    
    i = 0
    a  = list(res_a['experience'])
    b  = list(res_b['experience'])
    while i < len(a):
        if a[i] == 0 and b[i] == 0:
            a.pop(i)
            b.pop(i)
        i = i + 1
        
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 1.
        
    value = spatial.distance.cosine(a, b)
    return value


def lang_compare(res_a, res_b):
    if len(res_a['lang']) != len(res_b['lang']):
        raise('Unequal vectors exception')
    
    i = 0
    a  = list(res_a['lang'])
    b  = list(res_b['lang'])
    while i < len(a):
        if a[i] == 0 and b[i] == 0:
            a.pop(i)
            b.pop(i)
        i = i + 1
        
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 1.
    
    value = spatial.distance.cosine(a, b)
    return value if value != np.nan else 1


def skills_compare(res_a, res_b):
    if len(res_a['skills']) != len(res_b['skills']):
        raise('Unequal vectors exception')
    
    i = 0
    a  = list(res_a['skills'])
    b  = list(res_b['skills'])
    while i < len(a):
        if a[i] == 0 and b[i] == 0:
            a.pop(i)
            b.pop(i)
        i = i + 1
        
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 1.
    
    value = spatial.distance.cosine(a, b)
    return value
