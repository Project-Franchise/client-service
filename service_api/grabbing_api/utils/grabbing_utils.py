from service_api import Base
from service_api.models import RealtyDetails, Realty
from service_api.schemas import RealtySchema, RealtyDetailsSchema
import os
import sys
from json import JSONDecodeError
from typing import Dict, List, Tuple

import requests
from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta

sys.path.append(os.getcwd())
from service_api.grabbing_api.constants import (DOMRIA_API_KEY, DOMRIA_DOMAIN,
                                                DOMRIA_UKR, DOMRIA_URL,
                                                REALTY_DETAILS_KEYS,
                                                REALTY_KEYS)
from service_api.grabbing_api.resources import session_scope


def load_data(data: Dict, Model: Base, ModelSchema: SchemaMeta) -> SchemaMeta:
    """
    Stores data in a database according to a given scheme
    """

    try:
        valid_data = ModelSchema().load(data)
        record = Model(**valid_data)
    except ValidationError as error:
        print(error.messages)
        print("Validation failed", 400)
        raise ValidationError(error.args)
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

    realty_details_data = {
        key: value for (key, value) in
        zip(
            self_keys, original_keys
        )
    }

    return realty_details_data


def make_realty_data(response: requests.models.Response, realty_keys: List) -> Dict:
    """
    Composes data for Realty model
    """
    realty_data = dict()
    with session_scope() as session:
        for keys in realty_keys:
            id, model, response_key = keys
            realty_data[id] = (session.query(model).filter(
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
            raise JSONDecodeError(error.args)

        load_data(realty_details_data, RealtyDetails, RealtyDetailsSchema)

        try:
            realty_data = make_realty_data(response, REALTY_KEYS)
        except JSONDecodeError as error:
            raise JSONDecodeError(error.args)

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
