"""
Sending requests to Domria
"""
from typing import Dict

import requests

from .constants import DOMRIA_TOKEN, GE, LE


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
                char_description = metadata["model_characteristics"]["realty_details_columns"]
                if isinstance(value, dict):
                    value_from = value.get("values")[GE]
                    value_to = value.get("values")[LE]

                    key_from = char_description[value.get("name")]["ge"].format(value_from=str(parameter))
                    key_to = char_description[value.get("name")]["le"].format(value_to=str(parameter))

                    new_params[key_from] = value_from
                    new_params[key_to] = value_to
                else:
                    key = char_description[value.get("name")]["eq"].format(value_from=str(parameter))
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
