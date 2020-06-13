from datetime import datetime
from bindings import database
from bson import ObjectId


database['posts'].update_many({'_id': ObjectId('5e92f8b03bc187865692b516')}, {'$push': {'watchout': {''}}})
posts = database['users'].find({}, {'resume': 0})
print([x for x in posts][2])
