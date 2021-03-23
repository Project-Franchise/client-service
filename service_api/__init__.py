from flask import Flask
from flask_restful import Api
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from sqlalchemy import create_engine, MetaData
import redis

# initialisation of flask base app
flask_app = Flask(__name__)
flask_app.config.from_object('config.DevelopmentConfig')

# creating variable for building routes using flask_restful
api_ = Api(flask_app)

# connecting to DB
engine = create_engine(os.environ["DATABASE_URL"])
metadata = MetaData()
Base = declarative_base(metadata)
Session = sessionmaker(bind=engine)

# entrypoint for caching using redis
cache = redis.Redis(
    host=os.environ['REDIS_IP'], port=os.environ['REDIS_PORT'])

from . import models
from service_api.client_api import resources
