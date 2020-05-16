
from bindings import database

#users = database['posts'].update_one({'title': 'Java EE Formation'}, {"$set": {"ownerId": "ABCInfo"}})
#database['posts'].delete_one({'title': 'Java EE Formation'})
posts = database['companies'].find({})
print([x for x in posts])