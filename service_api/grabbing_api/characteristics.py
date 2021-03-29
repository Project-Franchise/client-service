import json
from typing import Dict

import requests

import constants

from pprint import pprint


def decode_characteristics(dct: Dict) -> Dict:
    item_list = {}
    if not 'items' in dct:
        return dct
    if 'items' in dct:
        for fields in dct['items']:
            if 'field_name' in fields:
                item_list.update(
                    {fields['field_name']: fields['characteristic_id']})
        return item_list
    return dct


def get_characteristics(characteristics: Dict = dict()) -> Dict:
    with open('service_api\static data\main_hardcode.json') as json_file:
        сharacteristics_data_set = json.load(json_file)
    for element in сharacteristics_data_set['realty_type']:
        req = requests.get(
            constants.DOMRIA_DOMAIN + constants.DOMRIA_URL["options"],
            params={"realty_type": сharacteristics_data_set['realty_type'][element],
                    "operation_type": 1,
                    "api_key": constants.DOMRIA_API_KEY})
        listik = req.json(object_hook=decode_characteristics)
        listik = [element for element in listik if element != {}]
        dictik = {}
        for i in listik:
            dictik.update(i)
        characteristics.update({element: dictik})
    return characteristics
