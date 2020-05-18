
from bindings import database

users = database['posts'].update_many({}, {"$set": {"comments": []}})
#database['posts'].delete_one({'title': 'Java EE Formation'})
posts = database['posts'].find({})
print([x for x in posts][0])