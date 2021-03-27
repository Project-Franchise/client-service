from flask import Flask
from flask_restful import Api, output_json
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from sqlalchemy import create_engine, MetaData


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

engine = create_engine(os.environ["DATABASE_URL"])
metadata = MetaData()
Base = declarative_base(metadata)
Session = sessionmaker(bind=engine)


from . import models
from service_api.client_api import resources
from service_api.grabbing_api import resources
