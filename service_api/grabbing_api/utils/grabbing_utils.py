"""
Utilities for creating models and saving them in DB
"""

import json
from typing import Dict, List, Union

from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta

from service_api import session_scope, Base
from service_api.errors import BadRequestException


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
        session.commit()
    return record[0]


def open_metadata(path: str) -> Dict:
    """
    Open file with metadata and return content
    """
    try:
        with open(path) as meta_file:
            metadata = json.load(meta_file)
    except json.JSONDecodeError as err:
        print(err)
        raise
    except FileNotFoundError:
        print("Invalid metadata path, or metadata.json file does not exist")
        raise
    return metadata
