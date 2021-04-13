"""
Sending requests to Domria
"""
from typing import Dict

import requests

from .constants import DOMRIA_TOKEN


class RealtyRequesterToServiceResource:
    """
    Send requests for getting list of id of items
    """

    @staticmethod
    def build_new_dict(params: dict, metadata: Dict) -> dict:
        """
        Method, that forms dictionary with parameters for the request
        ::
        """
        new_params = {}
        for parameter, value in params.items():
            if isinstance(parameter, int):
                if isinstance(params.get(parameter), dict):
                    value_from = value.get("values")["from"]  # constrains
                    value_to = value.get("values")["to"]

                    char_description = metadata["model_characteristics"]["realty_details_columns"]
                    key_from = char_description[value.get("name")]["gte"].format(value_from=str(parameter))
                    key_to = char_description[value.get("name")]["lte"].format(value_to=str(parameter))

                    new_params[key_from] = value_from
                    new_params[key_to] = value_to
                else:
                    key = "characteristic%5B" + str(parameter) + "%5D"  # f""
                    new_params[key] = value
            else:
                new_params[parameter] = params.get(parameter)
        return new_params

    def get(self, params: Dict, metadata: Dict) -> Dict:
        """
        Get all items from DOMRIA by parameters
        :return: Dict
        """
        new_params = self.build_new_dict(params, metadata)

        new_params["api_key"] = DOMRIA_TOKEN  # RESOURCE_ID
        url = "{base_url}{search}".format(
            base_url=metadata["base_url"],
            search=metadata["url_rules"]["search"]["url_prefix"],
        )
        response = requests.get(url=url, params=new_params, headers={'User-Agent': 'Mozilla/5.0'})

        # if response.status_code == 200:
        items_json = response.json()
        return items_json

# "price": {
#     "response_key": "price",
#     "gte": "characteristic%5B{value_from}%5D%5Bfrom%5D",
#     "lte": "characteristic%5B{value_to}%5D%5Bto%5D"
#   }
