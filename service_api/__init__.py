import os

import redis
from flask import Flask
from flask_restful import Api, output_json
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class UnicodeApi(Api):

    def __init__(self, *args, **kwargs):
        super(UnicodeApi, self).__init__(*args, **kwargs)
        self.app.config["RESTFUL_JSON"] = {
            "ensure_ascii": False
        }
        self.representations = {
            "application/json; charset=utf-8": output_json
        }


flask_app = Flask(__name__)
flask_app.config.from_object("config.DevelopmentConfig")
api_ = UnicodeApi(flask_app)

# connecting to DB
engine = create_engine(os.environ["DATABASE_URL"])
metadata = MetaData()
Base = declarative_base(metadata)
Session = sessionmaker(bind=engine)
session = Session()

# entrypoint for caching using redis
CACHE = redis.Redis(
    host=os.environ["REDIS_IP"], port=os.environ["REDIS_PORT"])

from service_api import client_api, grabbing_api

from . import models
