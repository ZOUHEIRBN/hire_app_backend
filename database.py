from datetime import datetime
from bindings import database
from bson import ObjectId
from business_methods import User


# database['users'].update_many({'resume': {'$exists': False}}, {'$set': {'resume': {
#     'academic_cursus': [],'academic_projects': [],'professionnal_cursus': [],'languages': [],'skills': []
# }}})
from business_methods.Post import set_user_watchouts

# set_user_watchouts('5e92f8b03bc187865692b516')
# posts = database['posts'].update_many({'type': 'offer'}, {'$set': {'type': 'Offer'}})
posts = database['posts'].find({})
print(set([x['type'] for x in posts]))

