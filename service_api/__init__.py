from flask import Flask
from flask_restful import Api
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from sqlalchemy import create_engine, MetaData


flask_app = Flask(__name__)
flask_app.config.from_object('config.DevelopmentConfig')
api_ = Api(flask_app)

engine = create_engine(os.environ["DATABASE_URL"])
metadata = MetaData()
Base = declarative_base(metadata)
Session = sessionmaker(bind=engine)


from . import models
from service_api.client_api import resources
