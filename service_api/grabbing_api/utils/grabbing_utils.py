"""
Utilities for creating models and saving them in DB
"""

import json
from functools import singledispatch
from typing import Dict, List, Union

from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta, Schema
from service_api import Base, models, session_scope
from service_api.models import Realty, RealtyDetails
from service_api.errors import BadRequestException
from service_api.exceptions import AlreadyInDbException
from service_api.grabbing_api.constants import DOMRIA_TOKEN
from service_api.schemas import RealtyDetailsSchema, RealtySchema
import datetime
from service_api.exceptions import ModelNotFoundException, ObjectNotFoundException, MetaDataError

@singledispatch
def load_data(model_schema: Schema, data: Dict, model: Base) -> Base:
    """
    Stores data in a database according to a given scheme
    """
    try:
        valid_data = model_schema.load(data)
        record = model(**valid_data)
    except ValidationError as error:
        print(error)
        raise

    with session_scope() as session:
        session.add(record)
    return record

@load_data.register
def _(model_schema: RealtyDetailsSchema, data: Dict, model: RealtyDetails):
    try:
        valid_data = model_schema.load(data)
        realty_details_record = model(**valid_data)  
    except ValidationError as error:
        print(error)
        raise
    with session_scope() as session:
        realty_details = session.query(model).filter_by(
            original_id=realty_details_record.original_id, version=realty_details_record.version).first()

    if realty_details is not None:
        print("version: ", realty_details.version)
        incoming_data = model_schema.dump(realty_details_record)
        db_data = model_schema.dump(realty_details)
        incoming_data.pop("id")
        db_data.pop("id")
        if incoming_data == db_data:
            raise AlreadyInDbException
        with session_scope() as session:
            print("they aren't equal")
            session.expire_on_commit = False
            session.query(model).filter_by(
                original_id=realty_details.original_id, version=realty_details.version).update(
                {"version": datetime.datetime.now()})
            session.add(realty_details_record)
            session.commit()
            realty_record = session.query(Realty).filter_by(
                realty_details_id=realty_details.id).first()
            new_realty_details_id = session.query(model).filter_by(
                original_id=realty_details_record.original_id, version=realty_details_record.version).first().id
            session.expunge(realty_record)
            del realty_record.id
            realty_record.realty_details_id = new_realty_details_id          
            print("needed id: ", model_schema.dump(realty_details).get("id"))
            session.query(Realty).filter_by(
                realty_details_id=model_schema.dump(realty_details).get("id")).update(
                {"version": datetime.datetime.now()})           
            session.add(realty_record)
        with session_scope() as session:
            session.query(Realty).filter_by(
                realty_details_id=model_schema.dump(realty_details).get("id")).update(
                {"version": datetime.datetime.now()})
    with session_scope() as session:
        session.add(realty_details_record)
    return realty_details_record
    #     session.add_all(record)

    # return record[0]


def open_metadata(path: str) -> Dict:
    """
    Open file with metadata and return content
    """
    try:
        with open(path) as meta_file:
            metadata = json.load(meta_file)
    except json.JSONDecodeError as error:
        print(error)
        raise MetaDataError from error
    except FileNotFoundError as error:
        print("Invalid metadata path, or metadata.json file does not exist")
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
        print(error)
        raise ModelNotFoundException(desc=f"Model {model} doesn't have aliases attribute") from error

    with session_scope() as session:
        set_ = set_ or session.query(model).join(table_of_aliases)
        obj = set_.filter(table_of_aliases.alias == alias).first()

    if obj is None:
        raise ObjectNotFoundException(desc=f"Record for alias: {alias} not found")
    return obj
