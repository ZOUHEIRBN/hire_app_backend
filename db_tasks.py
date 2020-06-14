from celery import Celery

import business_methods.Post as p


celery = Celery('Hire_Celery', broker_url='amqp://localhost//',
    backend='rpc://localhost//')

celery.conf.update({
    'task_serializer ': 'json',
    'result_serializer ': 'json',
    'accept_content ': ['pickle', 'json', 'msgpack']

})



@celery.task(name="post.set_watchouts")
def set_user_watchouts(job_id):
    return p.set_user_watchouts(job_id)
