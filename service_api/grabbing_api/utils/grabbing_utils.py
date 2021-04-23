"""
Utilities for creating models and saving them in DB
"""

import json
from typing import Dict, List, Union

from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta

from service_api import session_scope, Base
from service_api.errors import BadRequestException
from service_api.exceptions import ModelNotFoundException, ObjectNotFoundException, MetaDataError


def load_data(data: Union[Dict, List], model: Base, model_schema: SchemaMeta) -> SchemaMeta:
    """
    Stores data in a database according to a given scheme
    """
    try:
        if isinstance(data, dict):
            data = [data]
        valid_data = model_schema(many=True).load(data)
        record = [model(**data) for data in valid_data]
    except ValidationError as error:
        raise BadRequestException(error.args) from error

    with session_scope() as session:
        session.add_all(record)

    return record[0]


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
