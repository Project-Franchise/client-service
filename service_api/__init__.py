"""
Module that contains client_api, grabbing_api, models, schemas
"""

import os
from contextlib import contextmanager
from typing import Iterator

import redis
from flask import Flask
from flask_restful import Api, output_json
from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker, Session


class UnicodeApi(Api):
    """
    Redefined Api classs to suppoer unicode text responses
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
Session_factory = sessionmaker(bind=engine)
session = Session_factory()

# entrypoint for caching using redis
CACHE = redis.Redis(
    host=os.environ["REDIS_IP"], port=os.environ["REDIS_PORT"])


@contextmanager
def session_scope() -> Iterator[Session]:
    """
    Context manager to handle tranaction to DB
    """
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    else:
        try:
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise


from . import client_api, grabbing_api
