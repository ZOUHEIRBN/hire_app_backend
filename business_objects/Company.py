from bson import ObjectId

from bindings import database
def clean_id(x):
    if '_id' in x.keys():
        x['id'] = str(x['_id'])
        del x['_id']

    elif x['id'] is not None:
        x['id'] = str(x['id'])

    return x
def preprocess(x, requester_id=None):
    x = clean_id(x)
    if requester_id and requester_id != '0':
        requester = dict(database['users'].find_one({'_id': ObjectId(requester_id)},
                                                    {'_id': 1, 'email': 1, "following": 1}
                                                    ))

        x["badges"] = []
        if x == requester:
            return x

        if {'id': ObjectId(x['id'])} in requester["following"]:
            x["badges"].append({"category": "social", "name": "You follow"})

        if True:
            x["badges"].append({"category": "match", "name": "Watchout"})

    return x

def get_data(query, requester_id=None, return_unique=None):
    companies = database['companies'].find(query, {'password': 0})
    companies = [preprocess(x, requester_id) for x in companies]

    if return_unique is False:
        return {'body': companies}
    if len(companies) == 1:
        return companies[0]
    return {'body': companies}
