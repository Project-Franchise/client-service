"""
Handler module docstring for pylint
"""
import json
from abc import ABC, abstractmethod
from typing import Dict, List

from service_api import LOGGER
from service_api.utils import send_request
from service_api.async_logic import get_all_responses
from service_api.exceptions import  (MetaDataError, ObjectNotFoundException, ServiceHandlerError)
from service_api.grabbing_api.utils.services_convertors import (DomRiaInputConverter, DomRiaOutputConverter)
from .limitation import DomriaLimitationSystem




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
        try:
            search_realty_metadata, service_name = self.metadata["urls"]["search_realty"], self.metadata["name"]
        except KeyError as error:
            raise MetaDataError from error

        url = "{base_url}{condition}{search}".format(
            base_url=self.metadata["base_url"],
            condition=search_realty_metadata["condition"],
            search=search_realty_metadata["url_prefix"],
        )

        params = DomRiaInputConverter(self.post_body, search_realty_metadata, service_name=service_name).convert()
        for param, val in search_realty_metadata["optional"].items():
            params[param] = val
        params[self.metadata["token_name"]] = DomriaLimitationSystem.get_token()
        response = send_request("GET", url=url, params=params, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            raise ServiceHandlerError("Invalid url")

        items = response.json()
        try:
            return DomriaServiceHandler.process_request(items, self.post_body["additional"].pop("page"),
                                                        self.post_body["additional"].pop("page_ads_number"),
                                                        self.metadata)
        except KeyError as error:
            LOGGER.error(error.args)
            raise ServiceHandlerError(error.args) from error

    @staticmethod
    def create_records(ids: List, service_metadata: Dict) -> List[Dict]:
        """
        Creates records in the database on the ID list
        """
        params = {"api_key": DomriaLimitationSystem.get_token()}
        for param, val in service_metadata["optional"].items():
            params[param] = val

        url = "{base_url}{condition}{single_ad}".format(
            base_url=service_metadata["base_url"],
            single_ad=service_metadata["urls"]["single_ad"]["url_prefix"],
            condition=service_metadata["urls"]["single_ad"]["condition"]
        )
        realty_realty_details = []
        responses_container = get_all_responses(url, params, ids)
        for response in responses_container:
            if not response.ok:
                LOGGER.error("REsponse from Domria not ok: %s", response.content)
                continue
            service_converter = DomRiaOutputConverter(response.json(), service_metadata)

            try:
                realty_details = service_converter.make_realty_details_data()
            except json.JSONDecodeError:
                LOGGER.error("An error occurred while converting data from Dom Ria for realty_details model")
                continue
            except ObjectNotFoundException as error:
                LOGGER.error("Traceback: %s", error.__traceback__)
                continue

            try:
                realty_data = service_converter.make_realty_data()
            except json.JSONDecodeError:
                LOGGER.error("An error occurred while converting data from Dom Ria for realty model")
                continue
            except ObjectNotFoundException as error:
                LOGGER.error("Traceback: %s", error.__traceback__)
                continue
            realty_realty_details.append((realty_data, realty_details))
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
