"""
Module with abstract interfaces for classes need to communicate with services
"""
from abc import ABC, abstractmethod
from typing import Dict
from ..exceptions import BadFiltersException

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

class AbstractInputConverter(ABC):
    """
    Abstract class for input converters
    """

    def __init__(self, post_body: Dict, service_metadata: Dict, service_name):
        """
        Sets self values and except parsing errors
        """
        self.search_realty_metadata = service_metadata
        self.service_name = service_name
        try:
            self.characteristics = post_body["characteristics"]
            self.realty = post_body["realty_filters"]
            self.additional = post_body["additional"]
        except KeyError as error:
            raise BadFiltersException(error.args) from error

    @abstractmethod
    def convert(self):
        """
        Get all items from service by parameters
        :return: str
        :return: Dict
        """


class AbstractOutputConverter(ABC):
    """
    Abstract class for output converters
    """

    def __init__(self, response: Dict, service_metadata: Dict):
        """
        Sets self values
        """
        self.response = response
        self.service_metadata = service_metadata

    @abstractmethod
    def make_realty_data(self) -> Dict:
        """
        Converts a response to a dictionary ready for writing realty in the database
        """

    @abstractmethod
    def make_realty_details_data(self):
        """
        Converts a response to a dictionary ready for writing realty_details in the database
        """
