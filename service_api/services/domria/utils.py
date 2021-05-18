"""
Module with additional utils for domria
"""

from typing import Dict

from service_api import LOGGER

from ...constants import PATH_TO_METADATA
from ...exceptions import MetaDataError
from ...utils import open_metadata, send_request
from .limitation import DomriaLimitationSystem


class DomriaCharacteristicLoader:
    """
    Loader for domria characteristics
    """

    def __init__(self) -> None:
        try:
            self.metadata = open_metadata(PATH_TO_METADATA)["DOMRIA API"]
        except MetaDataError:
            LOGGER.error("Couldn't load metadata")

    @staticmethod
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

    def load(self, characteristics: Dict = None) -> Dict:
        """
        Function to get characteristics
        and retrieve them in dict
        """

        if characteristics is None:
            characteristics = {}

        chars_metadata, realty_types = self.metadata["urls"]["options"], self.metadata["entities"]["realty_type"]

        params = {"api_key": DomriaLimitationSystem.get_token()}

        for param, val in self.metadata["optional"].items():
            params[param] = val
        params["operation_type"] = 1

        for element in self.metadata["entities"]["realty_type"]:
            url = "{base_url}{condition}{options}".format(
                base_url=self.metadata["base_url"],
                condition=chars_metadata["condition"],
                options=chars_metadata["url_prefix"]
            )

            params[chars_metadata["fields"]["realty_type"]] = realty_types[element]
            req = send_request("GET", url=url, params=params, headers={'User-Agent': 'Mozilla/5.0'})

            requested_characteristics = req.json(object_hook=self.decode_characteristics)
            requested_characteristics = [
                element for element in requested_characteristics if element != {}
            ]

            named_characteristics = {}
            for character in requested_characteristics:
                named_characteristics.update(character)
            characteristics.update({element: named_characteristics})
        return characteristics
