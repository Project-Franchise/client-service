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

from .config import config_factory


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


engine, Base, session, API = None, declarative_base(), None, None

# entrypoint for caching using redis
CACHE = redis.Redis(
    host=os.environ["REDIS_IP"], port=os.environ["REDIS_PORT"], decode_responses=True)


def init_engine(url, **kwargs):
    global engine
    engine = create_engine(url)
    return engine


def init_db(engine):
    global Base
    metadata = MetaData(bind=engine)
    Base.metadata = metadata


def init_session(engine):
    global session
    session_factory = sessionmaker(bind=engine)
    session = session_factory()


def make_app(config="development"):
    print("!!!!")
    flask_app = Flask(__name__)
    print("!!!!")
    with flask_app.app_context():
        flask_app.config.from_object(config_factory.get(config))

        engine = init_engine(flask_app.config.get("SQLALCHEMY_DATABASE_URL"))
        init_db(engine)
        init_session(engine)

        global API
        API = UnicodeApi(flask_app)

        from . import client_api, grabbing_api, celery_tasks

    return flask_app


@contextmanager
def session_scope() -> Iterator[Session]:
    """
    Context manager to handle transaction to DB
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
