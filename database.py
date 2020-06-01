from datetime import datetime
from bindings import database
from bson import ObjectId


#users = database['posts'].update_one({'_id': ObjectId('5e92f8b03bc187865692b515')}, {})
# database['questions'].update_many({}, {'$set': {'asker': '5e92f8b03bc187865692b517'}})
posts = database['questions'].find({})
print([x for x in posts])
