"""
Sending requests to Domria
"""
import requests

from .constants import DOMRIA_API_KEY, DOMRIA_DOMAIN, DOMRIA_URL


class RealtyRequesterToDomria():
    """
    Send requests for getting list of id of items
    """

    @staticmethod
    def form_new_dict(params: dict) -> dict:
        """
        Method, that forms dictionary with parameters for the request
        """
        new_params = {}
        for key, value in params.items():
            if isinstance(key, int):
                if isinstance(value, dict):
                    new_key_from = "characteristic[{}][from]".format(key)
                    new_key_to = "characteristic[{}][to]".format(key)
                    new_params[new_key_from] = value.get("from")
                    new_params[new_key_to] = value.get("to")
                else:
                    new_key = "characteristic[{}]".format(key)
                    new_params[new_key] = value
            else:
                new_params[key] = value
        return new_params

    def get(self, params: dict) -> dict:
        """
        Get all items from DOMRIA by parameters
        :return: Dict
        """

        new_params = self.form_new_dict(params)

        new_params["api_key"] = DOMRIA_API_KEY

        response = requests.get(DOMRIA_DOMAIN + DOMRIA_URL["search"],
                                params=new_params)

        items_json = response.json()
        return items_json
