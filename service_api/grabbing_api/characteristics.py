"""
Main logic for getting characteristics from domria_api
"""
import datetime
import json
from typing import Dict

import requests
from redis import RedisError

from service_api import models, CACHE, session_scope
from service_api.errors import BadRequestException
from .constants import PATH_TO_METADATA, DOMRIA_TOKEN
from .utils.grabbing_utils import open_metadata


def decode_characteristics(dct: Dict) -> Dict:
    """
    Custom object hook.
    Used for finding characteristics
    in "items" dict
    """
    items = {}
    if "items" in dct:
        for fields in dct["items"]:
            if "field_name" in fields:
                items[fields["field_name"]] = fields["characteristic_id"]
        return items
    return dct


def get_characteristics(metadata: Dict, characteristics: Dict = None) -> Dict:
    """
    Function to get characteristics
    and retrieve them in dict
    """

    if characteristics is None:
        characteristics = {}

    characteristics_data_set = open_metadata(PATH_TO_METADATA)["DOMRIA API"]["url_characteristics"]

    params = {"api_key": DOMRIA_TOKEN}
    for param, val in metadata["optional"].items():
        params[param] = val
    params["operation_type"] = 1

    for element in characteristics_data_set["realty_type"]:
        url = "{base_url}{options}".format(
            base_url=metadata["base_url"],
            options=metadata["url_rules"]["options"]["url_prefix"]
        )

        params["realty_type"] = characteristics_data_set["realty_type"][element]
        req = requests.get(
            url=url,
            params=params,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        requested_characteristics = req.json(object_hook=decode_characteristics)
        requested_characteristics = [
            element for element in requested_characteristics if element != {}
        ]

        named_characteristics = {}
        for character in requested_characteristics:
            named_characteristics.update(character)
        characteristics.update({element: named_characteristics})
    return characteristics


def process_characteristics(service_metadata: Dict, realty: Dict, redis_ex_time: Dict, redis_characteristics: str):
    """
    Retrieves data from Redis and converts it to the required format for the request
    """
    cached_characteristics = CACHE.get(redis_characteristics)
    if cached_characteristics is None:
        try:
            characteristics = get_characteristics(metadata=service_metadata)
            CACHE.set(redis_characteristics,
                      json.dumps(characteristics),
                      datetime.timedelta(**redis_ex_time))
        except json.JSONDecodeError as error:
            raise json.JSONDecodeError from error
        except RedisError as error:
            raise RedisError(error.args) from error
    else:
        characteristics = json.loads(cached_characteristics)

    with session_scope() as session:
        realty_type = session.query(models.RealtyType).get(
            realty.get("realty_type_id"))

    if realty_type is None:
        raise BadRequestException("Invalid realty_type while getting latest data")

    try:
        type_mapper = characteristics.get(realty_type.name)
    except Exception as error:
        print(error)
        raise

    return type_mapper
