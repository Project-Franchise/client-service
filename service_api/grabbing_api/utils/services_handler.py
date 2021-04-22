"""
Handler module docstring for pylint
"""
import json
from typing import List, Dict
from abc import ABC, abstractmethod

import requests

from service_api.grabbing_api.utils.services_convertors import DomRiaOutputConverter, DomRiaInputConverter
from service_api.errors import BadRequestException
from service_api.grabbing_api.constants import DOMRIA_TOKEN


class AbstractServiceHandler(ABC):
    """
    Abstract class for handler class
    """

    def __init__(self, post_body: Dict, service_metadata: Dict):
        """
        Sets self values
        """
        self.metadata = service_metadata
        self.post_body = post_body

    @abstractmethod
    def get_latest_data(self):
        """
        Method that realise the logic of sending request to particular service and getting items
        """


class DomriaServiceHandler(AbstractServiceHandler):
    """
    Handler class for DomRia service
    """

    def get_latest_data(self):
        """
        Method that realise the logic of sending request to DomRia and getting items
        :return: List(dict)
        """
        url, params = DomRiaInputConverter(self.post_body, self.metadata).convert()

        response = requests.get(url=url, params=params, headers={'User-Agent': 'Mozilla/5.0'})
        # if response.status_code == 200:
        items = response.json()
        try:
            return DomriaServiceHandler.process_request(items, self.post_body["additional"].pop("page"),
                                                        self.post_body["additional"].pop("page_ads_number"),
                                                        self.metadata)
        except KeyError as error:
            print(error.args)
            raise BadRequestException(error.args) from error

    @staticmethod
    def create_records(ids: List, service_metadata: Dict) -> List[Dict]:
        """
        Creates records in the database on the ID list
        """
        params = {"api_key": DOMRIA_TOKEN}
        for param, val in service_metadata["optional"].items():
            params[param] = val

        url = "{base_url}{single_ad}{condition}".format(
            base_url=service_metadata["base_url"],
            single_ad=service_metadata["url_rules"]["single_ad"]["url_prefix"],
            condition=service_metadata["url_rules"]["single_ad"]["condition"]
        )
        realty_realty_details = []
        for realty_id in ids:
            response = requests.get("{url}{id}".format(url=url, id=str(realty_id)),
                                    params=params,
                                    headers={'User-Agent': 'Mozilla/5.0'})

            service_converter = DomRiaOutputConverter(response, service_metadata)
            try:
                realty_details = service_converter.make_realty_details_data()
            except json.JSONDecodeError:
                print("An error occurred while converting data from Dom Ria for realty_details model")
                raise

            try:
                realty_data = service_converter.make_realty_data(realty_details)
            except json.JSONDecodeError:
                print("An error occurred while converting data from Dom Ria for realty model")
                raise

            realty_realty_details.append(realty_data)

        return realty_realty_details


    @staticmethod
    def process_request(search_response: Dict, page: int, page_ads_number: int, metadata: Dict) -> List[Dict]:
        """
        Distributes a list of ids to write to the database and return to the user
        """
        page = page % page_ads_number
        current_items = search_response["items"][
                        (page + 1) * page_ads_number - page_ads_number: (page + 1) * page_ads_number
                        ]

        return DomriaServiceHandler.create_records(current_items, metadata)
