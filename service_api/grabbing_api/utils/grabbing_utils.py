import os
import sys
from typing import Dict, List, Tuple

import requests
from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta
from service_api import session
from service_api.schemas import RealtyDetailsSchema, RealtySchema
from service_api.grabbing_api.constants import (DOMRIA_API_KEY, DOMRIA_DOMAIN,
                                                DOMRIA_UKR, DOMRIA_URL,
                                                REALTY_DETAILS_KEYS,
                                                REALTY_KEYS)
from sqlalchemy.orm import Session
import json

sys.path.append(os.getcwd())

def load_data(data: Dict, session: Session, ModelSchema: SchemaMeta) -> SchemaMeta:
    """
    Stores data in a database according to a given scheme
    """
    try:
        res_data = ModelSchema().load(data)
    except ValidationError as error:
        print(error.messages)
        print("Validation failed", 400)
        return ModelSchema().load(dict())

    session.add(res_data)
    session.commit()
    return res_data


def make_realty_details_data(response: requests.models.Response, realty_details_keys: Dict) -> Dict:
    """
    Composes data for RealtyDetails model
    """
    original_keys = [response.json()[val] for val in realty_details_keys.values()]
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
    for keys in realty_keys:
        id, model, response_key = keys
        realty_data[id] = (session.query(model).filter(
            model.original_id == response.json()[response_key]
        ).first()).id

    return realty_data


def create_records(id_list: List, session: Session) -> List[Tuple[SchemaMeta, SchemaMeta]]:
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
        realty_details_data = make_realty_details_data(response, REALTY_DETAILS_KEYS)
        realty_details = load_data(realty_details_data, session, RealtyDetailsSchema)

        realty_data = make_realty_data(response, REALTY_KEYS)
        realty = load_data(realty_data, session, RealtySchema)

        schema = schemas.RealtySchema()
        elem = schema.dump(realty)

        realty_models.append(elem)

    return realty_models


def process_request(search_response: Dict, session: Session, page: int, page_ads_number: int) -> \
        list[tuple[SchemaMeta, SchemaMeta]]:
    """
    Distributes a list of ids to write to the database and return to the user
    """
    page = page % page_ads_number
    current_items = search_response["items"][
                    page * page_ads_number - page_ads_number: page * page_ads_number
                    ]

    return create_records(current_items, session)
