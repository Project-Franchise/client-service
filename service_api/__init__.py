"""
Module that contains client_api, grabbing_api, models, schemas
"""

import logging
import os
from contextlib import contextmanager
from typing import Iterator

import redis
from flask import Flask
from flask_restful import Api, output_json
from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from logs.logger import setup_logger


class UnicodeApi(Api):
    """
    Redefined Api class to suppose unicode text responses
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
flask_app.config.from_object(os.environ.get("FLASK_CONFIG_MODE", "config.DevelopmentConfig"))
api_ = UnicodeApi(flask_app)

# connecting to DB
engine = create_engine(flask_app.config.get("SQLALCHEMY_DATABASE_URL"))
metadata = MetaData(bind=engine)
Base = declarative_base(metadata)
Session_factory = sessionmaker(bind=engine)
session = Session_factory()

# entrypoint for caching using redis
CACHE = redis.Redis(
    host=os.environ["REDIS_IP"], port=os.environ["REDIS_PORT"], decode_responses=True)

LOGGER = setup_logger('app_logger', 'logs/service.log', logging.DEBUG)


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


from . import celery_tasks, client_api, commands, grabbing_api
