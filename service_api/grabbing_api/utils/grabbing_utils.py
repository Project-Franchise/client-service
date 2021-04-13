"""
Utilities for creating models and saving them in DB
"""

import json
from typing import Dict, List, Union

import requests
from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta

from service_api import models, session_scope, Base
from service_api.errors import BadRequestException
from service_api.grabbing_api.constants import DOMRIA_TOKEN
from service_api.schemas import RealtyDetailsSchema, RealtySchema


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


def make_realty_details_data(response: requests.models.Response, realty_details_meta: Dict) -> Dict:
    """
    Composes data for RealtyDetails model
    """

    data = response.json()

    keys = realty_details_meta.keys()
    values = [data.get(val["response_key"], None) for val in realty_details_meta.values()]

    realty_details_data = dict(zip(
        keys, values
    ))

    return realty_details_data


def make_realty_data(response: requests.models.Response, realty_keys: Dict) -> Dict:
    """
    Composes data for Realty model
    """
    realty_data = {}
    with session_scope() as session:
        for key, characteristics in realty_keys.items():
            model = characteristics["model"]
            response_key = characteristics["response_key"]

            model = getattr(models, model)

            if not model:
                raise Warning(f"There is no such model named {model}")

            realty_data[key] = (session.query(model).filter(
                model.original_id == response.json()[response_key]
            ).first()).id  # and service_name == service_name

    return realty_data


def create_records(id_list: List, service_metadata: Dict) -> List[Dict]:
    """
    Creates records in the database on the ID list
    """
    params = {"api_key": DOMRIA_TOKEN}
    for param, val in service_metadata["optional"].items():
        params[param] = val

    url = "{base_url}{single_ad}{condition}".format(
            base_url=service_metadata["base_url"],
            single_ad=service_metadata["url_rules"]["single_ad"]["url_prefix"],
            condition=service_metadata["url_rules"]["single_ad"]["condition"]
            )

    realty_models = []
    for realty_id in id_list:
        response = requests.get("{url}{id}".format(url=url, id=str(realty_id)),
                                params=params,
                                headers={'User-Agent': 'Mozilla/5.0'})

        try:
            realty_details_data = make_realty_details_data(
                response, service_metadata["model_characteristics"]["realty_details_columns"]
            )
        except json.JSONDecodeError as error:
            print(error)
            raise

        load_data(realty_details_data, models.RealtyDetails, RealtyDetailsSchema)

        try:
            realty_data = make_realty_data(response, service_metadata["model_characteristics"]["realty_columns"])
        except json.JSONDecodeError as error:
            print(error)
            raise

        realty = load_data(realty_data, models.Realty, RealtySchema)

        schema = RealtySchema()
        elem = schema.dump(realty)

        realty_models.append(elem)

    return realty_models


def process_request(search_response: Dict, page: int, page_ads_number: int, metadata: Dict) -> List[Dict]:
    """
    Distributes a list of ids to write to the database and return to the user
    """
    page = page % page_ads_number
    current_items = search_response["items"][
                    page * page_ads_number - page_ads_number: page * page_ads_number
                    ]

    return create_records(current_items, metadata)


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
