"""
Utilities for creating models and saving them in DB
"""

from json import JSONDecodeError
from typing import Dict, List

import requests
from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta
from service_api import Base
from service_api.errors import BadRequestException
from service_api.models import Realty, RealtyDetails
from service_api.schemas import RealtyDetailsSchema, RealtySchema

from service_api.grabbing_api.constants import (DOMRIA_API_KEY, DOMRIA_DOMAIN,
                                                DOMRIA_UKR, DOMRIA_URL,
                                                REALTY_DETAILS_KEYS,
                                                REALTY_KEYS)
from service_api.grabbing_api.resources import session_scope


def load_data(data: Dict, model: Base, model_schema: SchemaMeta) -> SchemaMeta:
    """
    Stores data in a database according to a given scheme
    """

    try:
        valid_data = model_schema().load(data)
        record = model(**valid_data)
    except ValidationError as error:
        raise BadRequestException from error
    with session_scope() as session:
        session.add(record)
        session.commit()
    return record


def make_realty_details_data(response: requests.models.Response, realty_details_keys: Dict) -> Dict:
    """
    Composes data for RealtyDetails model
    """

    data = response.json()

    original_keys = [data.get(val, None) for val in realty_details_keys.values()]
    self_keys = realty_details_keys.keys()

    realty_details_data = dict.fromkeys(
        self_keys, original_keys
    )

    return realty_details_data


def make_realty_data(response: requests.models.Response, realty_keys: List) -> Dict:
    """
    Composes data for Realty model
    """
    realty_data = dict()
    with session_scope() as session:
        for keys in realty_keys:
            key, model, response_key = keys
            realty_data[key] = (session.query(model).filter(
                model.original_id == response.json()[response_key]
            ).first()).id

    return realty_data


def create_records(id_list: List) -> List[Dict]:
    """
    Creates records in the database on the ID list
    """
    params = {
        "lang_id": DOMRIA_UKR,
        "api_key": DOMRIA_API_KEY,
    }

    url = DOMRIA_DOMAIN + DOMRIA_URL["id"]
    realty_models = []
    for realty_id in id_list:
        response = requests.get(url + "/" + str(realty_id), params=params)

        try:
            realty_details_data = make_realty_details_data(response, REALTY_DETAILS_KEYS)
        except JSONDecodeError as error:
            print(error)
            raise

        load_data(realty_details_data, RealtyDetails, RealtyDetailsSchema)

        try:
            realty_data = make_realty_data(response, REALTY_KEYS)
        except JSONDecodeError as error:
            print(error)
            raise

        realty = load_data(realty_data, Realty, RealtySchema)

        schema = RealtySchema()
        elem = schema.dump(realty)

        realty_models.append(elem)

    return realty_models


def process_request(search_response: Dict, page: int, page_ads_number: int) -> List[Dict]:
    """
    Distributes a list of ids to write to the database and return to the user
    """
    page = page % page_ads_number
    current_items = search_response["items"][
        page * page_ads_number - page_ads_number: page * page_ads_number
    ]
    return create_records(current_items)
