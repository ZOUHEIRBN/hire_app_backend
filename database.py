from datetime import datetime
from bindings import database
from bson import ObjectId
#users = database['posts'].update_one({'_id': ObjectId('5e92f8b03bc187865692b515')}, {})
#database['posts'].update_many({'type': 'Offer'}, {'$set': {'submissions': []}})
database['companies'].update_many({}, {'$unset': {'id': ''}})
posts = database['companies'].find({})
print([x for x in posts][0])