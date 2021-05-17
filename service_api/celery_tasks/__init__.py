"""
Module with celery tasks and configuration
"""
from service_api import flask_app
from .utils import make_celery

celery_app = make_celery(flask_app)
