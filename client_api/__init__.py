from flask import Flask
from flask_restful import Api
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import os


flask_app = Flask(__name__)
flask_app.config.from_object('config.DevelopmentConfig')
api_ = Api(flask_app)

engine = create_engine(os.environ["DATABASE_URL"])
Base = declarative_base()
Session = sessionmaker(bind=engine)

from . import resources
