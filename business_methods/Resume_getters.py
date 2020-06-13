# Global getters
from bindings import database

# Get all academic


def get_all_academic():
    _ac = [x['resume']['academic_cursus'] for x in database['users'].find({}) if
           'resume' in x.keys() and 'academic_cursus' in x['resume'].keys()]
    all_ac = []
    for e in _ac:
        all_ac.extend([x['title'] for x in e])

    _ac = [x['requiredDegrees'] for x in database['posts'].find({}) if 'requiredDegrees' in x.keys()]
    for e in _ac:
        all_ac.extend([x['option'] for x in e])

    return sorted(list(set(all_ac)))


# Get all experiences
def get_all_experiences():
    _xps = [x['resume']['professionnal_cursus'] for x in database['users'].find({}) if
            'resume' in x.keys() and 'professionnal_cursus' in x['resume'].keys()]
    all_xps = []
    for e in _xps:
        all_xps.extend([x['title'] for x in e])

    _xps = [x['requiredExp'] for x in database['posts'].find({}) if 'requiredExp' in x.keys()]
    for e in _xps:
        all_xps.extend([x['title'] for x in e])

    return sorted(list(set(all_xps)))


# Get all skills
def get_all_skills():
    _skills = [x['resume']['skills'] for x in database['users'].find({}) if
               'resume' in x.keys() and 'skills' in x['resume'].keys()]
    all_skills = []
    for e in _skills:
        all_skills.extend([x['skill'] for x in e])

    _skills = [x['requiredSkills'] for x in database['posts'].find({}) if 'requiredSkills' in x.keys()]
    for e in _skills:
        all_skills.extend([x['skill'] for x in e])

    return sorted(list(set(all_skills)))


# Get all languages
def get_all_languages():
    _languages = [x['resume']['languages'] for x in database['users'].find({}) if
                  'resume' in x.keys() and 'languages' in x['resume'].keys()]
    all_languages = []
    for e in _languages:
        all_languages.extend([x['lang'] for x in e])

    _languages = [x['requiredLanguages'] for x in database['posts'].find({}) if 'requiredLanguages' in x.keys()]
    for e in _languages:
        all_languages.extend([x['lang'] for x in e])

    return sorted(list(set(all_languages)))