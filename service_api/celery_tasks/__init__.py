"""
Module with celery tasks and configuration
"""
from service_api import flask_app
from service_api.celery_tasks.utils import make_celery

celery_app = make_celery(flask_app)
# celery_app.conf.beat_schedule = {
#     "taskkkk": {
#         "task": "service_api.celery_tasks.tasks.update_realties",
#         "schedule": 30.0
#     }
# }
