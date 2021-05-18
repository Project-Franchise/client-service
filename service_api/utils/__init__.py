"""
Utilities for creating models and saving them in DB
"""
import datetime
import json
from functools import singledispatch
from typing import Dict

from marshmallow import ValidationError
from marshmallow.schema import Schema
from requests import Session
from sqlalchemy.orm import make_transient
from sqlalchemy import func

from service_api import LOGGER, Base, session_scope
from ..exceptions import (MetaDataError, ModelNotFoundException, ObjectNotFoundException)
from ..models import Realty, RealtyDetails
from ..schemas import RealtyDetailsSchema, RealtySchema


@singledispatch
def load_data(model_schema: Schema, data: Dict, model: Base) -> Base:
    """
    Stores data in a database according to a given scheme
    """
    try:
        valid_data = model_schema.load(data)
        record = model(**valid_data)
    except ValidationError as error:
        LOGGER.error("Error message:%s, data for validation %s", error, valid_data)

        raise

    with session_scope() as session:
        existing_record = session.query(model).filter_by(**valid_data).first()
        if existing_record is None:
            session.add(record)
    return existing_record or record


@load_data.register
def _(model_schema: RealtyDetailsSchema, data: Dict, model: RealtyDetails):
    try:
        valid_data = model_schema.load(data)
        realty_details_record = model(**valid_data)
    except ValidationError as error:
        LOGGER.error(error)
        raise
    with session_scope() as session:
        realty_details = session.query(model).filter_by(
            original_url=realty_details_record.original_url, version=realty_details_record.version).first()

    if realty_details is not None:

        incoming_data = model_schema.dump(realty_details_record)
        db_data = model_schema.dump(realty_details)
        incoming_data.pop("id")
        db_data.pop("id")
        if incoming_data == db_data:
            return realty_details
        with session_scope() as session:

            session.expire_on_commit = False
            session.query(model).filter_by(
                original_url=realty_details.original_url, version=realty_details.version).update(
                {"version": datetime.datetime.now()})
            session.add(realty_details_record)
            session.commit()

            realty_record = session.query(Realty).filter_by(
                realty_details_id=realty_details.id).first()
            new_realty_details_id = session.query(model).filter_by(
                original_url=realty_details_record.original_url, version=realty_details_record.version).first().id

            make_transient(realty_record)
            realty_record.realty_details_id = new_realty_details_id
            realty_record.id = None
            del realty_record.id

            session.add(realty_record)

        with session_scope() as session:
            session.query(Realty).filter_by(
                realty_details_id=model_schema.dump(realty_details).get("id")).update(
                {"version": datetime.datetime.now()})
    with session_scope() as session:
        session.add(realty_details_record)
    return realty_details_record


@load_data.register
def _(model_schema: RealtySchema, data: Dict, model: Realty):
    try:
        valid_data = model_schema.load(data)
        realty_record = model(**valid_data)
        LOGGER.debug("record.realty_details_id: %s", str(realty_record.realty_details_id))
    except ValidationError as error:
        LOGGER.error(error)
        raise
    with session_scope() as session:
        realty = session.query(model).filter_by(realty_details_id=realty_record.realty_details_id).first()
    if realty is None:
        with session_scope() as session:
            session.add(realty_record)
    return realty or realty_record


def open_metadata(path: str) -> Dict:
    """
    Open file with metadata and return content
    """
    try:
        with open(path, encoding="utf-8") as meta_file:
            metadata = json.load(meta_file)
    except json.JSONDecodeError as error:
        LOGGER.error(error)
        raise MetaDataError from error
    except FileNotFoundError as error:
        LOGGER.error("Invalid metadata path, or metadata.json file does not exist")
        raise MetaDataError from error
    return metadata


def recognize_by_alias(model: Base, alias: str, set_=None):
    """
    Finds model record by alias. If set param is passed that alias is searched in that set
    :param model: Base
    :param alias: str
    :param set_: optional
    :returns: model instance
    :raises: ModelNotFoundException, ObjectNotFoundException
    """

    try:
        table_of_aliases = model.aliases.mapper.class_
    except AttributeError as error:
        LOGGER.error(error)
        raise ModelNotFoundException(desc="Model {} doesn't have aliases attribute".format(model)) from error

    with session_scope() as session:
        set_ = set_ or session.query(model)
        obj = set_.join(table_of_aliases, table_of_aliases.entity_id == model.id).filter(
            func.lower(table_of_aliases.alias) == alias.lower()).first()

    if obj is None:
        raise ObjectNotFoundException(message="Record for alias: {} not found".format(alias))
    return obj


def send_request(method: str, url: str, request_session: Session = None, *args, **kwargs):
    """
    Wrapper for sending requests
    """
    request_session = request_session or Session()
    response = request_session.request(method, url, *args, **kwargs)
    from ..services.limitation import LimitationSystem
    LimitationSystem().mark_token_after_request(response.url)
    return response
