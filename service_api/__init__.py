from flask import Flask
from flask_restful import Api
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from sqlalchemy import create_engine, MetaData

flask_app = Flask(__name__)
api_ = Api(flask_app)

engine = create_engine(os.environ["DATABASE_URL"])
metadata = MetaData()
Base = declarative_base(metadata)
Session = sessionmaker(bind=engine)

from . import views, models
