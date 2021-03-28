import os
from flask import Flask
from flask_restful import Api, output_json
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, MetaData
import redis


class UnicodeApi(Api):

    def __init__(self, *args, **kwargs):
        super(UnicodeApi, self).__init__(*args, **kwargs)
        self.app.config['RESTFUL_JSON'] = {
            'ensure_ascii': False
        }
        self.representations = {
            'application/json; charset=utf-8': output_json
        }


flask_app = Flask(__name__)
flask_app.config.from_object('config.DevelopmentConfig')
api_ = UnicodeApi(flask_app)

# connecting to DB
engine = create_engine(os.environ["DATABASE_URL"])
metadata = MetaData()
Base = declarative_base(metadata)
Session = sessionmaker(bind=engine)


# entrypoint for caching using redis
cache = redis.Redis(
    host=os.environ['REDIS_IP'], port=os.environ['REDIS_PORT'])

# entrypoint for caching using redis
CACHE = redis.Redis(
    host=os.environ['REDIS_IP'], port=os.environ['REDIS_PORT'])

from . import models
from service_api import client_api
from service_api import grabbing_api
