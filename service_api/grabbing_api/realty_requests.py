from . import constants
import requests


class RealtyRequestToDomria():
    """
    Send requests for getting list of id of items
    """

    @staticmethod
    def form_new_dict(params: dict) -> dict:
        """
        Method, that forms dictionary with parameters for the request
        """
        new_params = dict()
        for parameters in params:
            if isinstance(parameters, int):
                if isinstance(params.get(parameters), dict):
                    new_key_from = 'characteristic%5B' + \
                        str(parameters) + '%5D%5Bfrom%5D'
                    new_value_from = params[parameters].get("from")
                    new_key_to = 'characteristic%5B' + \
                        str(parameters) + '%5D%5Bto%5D'
                    new_value_to = params[parameters].get("to")
                    new_params[new_key_from] = new_value_from
                    new_params[new_key_to] = new_value_to
                else:
                    new_key = 'characteristic%5B' + str(parameters) + '%5D'
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

        params = {
            'category': 1,
            'realty_type': 2,
            'operation_type': 1,
            'state_id': 10,
            'city_id': 10,
            'district_id': [15187, 15189, 15188],
            209: {'from': 1, 'to': 3},
            214: {'from': 60, 'to': 90},
            216: {'from': 30, 'to': 50},
            218: {'from': 4, 'to': 9},
            227: {'from': 3, 'to': 7},
            443: 442,
            234: {'from': 20000, 'to': 90000},
            242: 239,
            273: 273,
            1437: 1434,
            'api_key': constants.DOMRIA_API_KEY,
        }

        new_params = self.form_new_dict(params)

        response = requests.get(constants.DOMRIA_DOMAIN +
                                constants.DOMRIA_URL["search"],
                                params=new_params)

        items_json = response.json()
        return items_json
