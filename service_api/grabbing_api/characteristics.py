"""
Main logic for getting characteristics from domria_api
"""

import json
from typing import Dict

import requests

from .constants import DOMRIA_API_KEY, DOMRIA_DOMAIN, DOMRIA_URL


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


def get_characteristics(characteristics: Dict = None) -> Dict:
    """
    Function to get characteristics
    and retrieve them in dict
    """

    if characteristics is None:
        characteristics = dict()

    with open("service_api/static data/main_hardcode.json") as json_file:
        characteristics_data_set = json.load(json_file)
    for element in characteristics_data_set["realty_type"]:
        req = requests.get(
            DOMRIA_DOMAIN + DOMRIA_URL["options"],
            params={"realty_type": characteristics_data_set["realty_type"][element],
                    "operation_type": 1,
                    "api_key": DOMRIA_API_KEY}, headers={'User-agent': 'Mozilla/5.0'})
        list_of_characteristics = req.json(object_hook=decode_characteristics)
        list_of_characteristics = [
            element for element in list_of_characteristics if element != {}]
        dict_of_characteristics = {}
        for i in list_of_characteristics:
            dict_of_characteristics.update(i)
        characteristics.update({element: dict_of_characteristics})
    return characteristics
