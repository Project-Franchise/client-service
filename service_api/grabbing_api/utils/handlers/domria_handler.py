"""
Handler module docstring for pylint
"""
import json
from typing import List, Dict

import requests

from service_api import models
from service_api.grabbing_api.constants import DOMRIA_TOKEN
from service_api.grabbing_api.utils.converters.domria_converter import DomRiaOutputConverter
from service_api.grabbing_api.utils.grabbing_utils import load_data
from service_api.schemas import RealtySchema, RealtyDetailsSchema


def create_records(ids: List, service_metadata: Dict) -> List[Dict]:
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
    for realty_id in ids:
        response = requests.get("{url}{id}".format(url=url, id=str(realty_id)),
                                params=params,
                                headers={'User-Agent': 'Mozilla/5.0'})

        service_converter = DomRiaOutputConverter(response, service_metadata)
        try:
            realty_details_data = service_converter.make_realty_details_data()
        except json.JSONDecodeError:
            print("An error occurred while converting data from Dom Ria for realty_details model")
            raise

        load_data(realty_details_data, models.RealtyDetails, RealtyDetailsSchema)

        try:
            realty_data = service_converter.make_realty_data()
        except json.JSONDecodeError:
            print("An error occurred while converting data from Dom Ria for realty model")
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
                    (page + 1) * page_ads_number - page_ads_number: (page + 1) * page_ads_number
                    ]

    return create_records(current_items, metadata)
