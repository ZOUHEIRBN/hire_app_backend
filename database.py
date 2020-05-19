from datetime import datetime
from bindings import database

users = database['posts'].update_many({}, {"$set": {"timestamp": str(datetime.now())}})
#database['posts'].delete_one({'title': 'Java EE Formation'})
posts = database['users'].find({})
print([x for x in posts][0])