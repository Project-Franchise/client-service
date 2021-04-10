"""
Sending requests to Domria
"""
import requests

from .constants import DOMRIA_API_KEY, DOMRIA_DOMAIN, DOMRIA_URL


class RealtyRequesterToDomriaResource:                    #Чи так можна???
    """
    Send requests for getting list of id of items
    """

    @staticmethod
    def build_new_dict(params: dict) -> dict:
        """
        Method, that forms dictionary with parameters for the request
        ::
        """
        new_params = {}
        for parameters in params:  # items
            if isinstance(parameters, int):
                if isinstance(params.get(parameters), dict):
                    new_key_from = "characteristic%5B" + str(parameters) + "%5D%5Bfrom%5D"  # f""
                    new_value_from = params[parameters].get("from")  # constrains
                    new_key_to = "characteristic%5B" + str(parameters) + "%5D%5Bto%5D"  # f""
                    new_value_to = params[parameters].get("to")
                    new_params[new_key_from] = new_value_from
                    new_params[new_key_to] = new_value_to
                else:
                    new_key = "characteristic%5B" + str(parameters) + "%5D"  # f""
                    new_value = params.get(parameters)
                    new_params[new_key] = new_value
            else:
                new_params[parameters] = params.get(parameters)
        return new_params

    def get(self, params: dict) -> dict:
        """
        Get all items from DOMRIA by parameters
        :return: Dict
        """

        new_params = self.build_new_dict(params)

        new_params["api_key"] = DOMRIA_API_KEY  # RESOURCE_ID

        response = requests.get(DOMRIA_DOMAIN + DOMRIA_URL["search"], params=new_params)

        # if response.status_code == 200:
        items_json = response.json()
        return items_json
