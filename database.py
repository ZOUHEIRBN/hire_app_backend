from datetime import datetime
from bindings import database
from bson import ObjectId


database['posts'].update_many({}, {'$set': {'comments': []}})
posts = database['posts'].find({}, {'imageUrl': 0})
print([x for x in posts][0])
