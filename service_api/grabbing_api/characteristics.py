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


def decode_characteristics(dct: Dict) -> Dict:
    """
    Custom object hook.
    Used for finding characteristics
    in "items" dict
    """
    item_list = {}
    if "items" in dct:
        for fields in dct["items"]:
            if "field_name" in fields:
                item_list[fields["field_name"]] = fields["characteristic_id"]
        return item_list
    return dct


def get_characteristics(metadata: Dict, characteristics: Dict = None) -> Dict:  # None {}
    """
    Function to get characteristics
    and retrieve them in dict
    """

    if characteristics is None:
        characteristics = dict()

    with open("service_api/static data/main_hardcode.json") as json_file:
        characteristics_data_set = json.load(json_file)

    params = {}
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

        list_of_characteristics = req.json(object_hook=decode_characteristics)
        list_of_characteristics = [
            element for element in list_of_characteristics if element != {}]
        dict_of_characteristics = {}
        for i in list_of_characteristics:
            dict_of_characteristics.update(i)
        characteristics.update({element: dict_of_characteristics})
    return characteristics


def process_characteristics(service_metadata: Dict, realty: Dict, redis_ex_time: Dict, redis_characteristics: str):
    """
    Retrieves data from Redis and converts it to the required format for the request
    """
    cached_characteristics = CACHE.get(redis_characteristics)  # >>>>>>
    if cached_characteristics is None:
        try:
            mapper = get_characteristics(metadata=service_metadata)
            CACHE.set(redis_characteristics,
                      json.dumps(mapper),
                      datetime.timedelta(**redis_ex_time))
        except json.JSONDecodeError as error:
            raise json.JSONDecodeError from error
        except RedisError as error:
            raise RedisError(error.args) from error
    else:
        mapper = json.loads(cached_characteristics)  # <<<<<<<<<

    with session_scope() as session:
        realty_type = session.query(models.RealtyType).get(
            realty.get("realty_type_id"))

    if realty_type is None:
        raise BadRequestException("Invalid realty_type while getting latest data")

    try:
        type_mapper = mapper.get(realty_type.name)
    except Exception as error:
        print(error)
        raise

    return type_mapper
