"""
Data updaters for keeping actual data
"""
import datetime
import json
from abc import ABC, abstractmethod
from typing import Dict

import requests
from sqlalchemy.engine.row import Row

from service_api import session_scope, models, schemas, LOGGER
from ..services.domria.limitation import DomriaLimitationSystem
from ..errors import InternalServerErrorException
from ..exceptions import ResponseNotOkException, MetaDataError
from ..constants import PATH_TO_METADATA
from ..utils import open_metadata, load_data
from ..services.domria.convertors import DomRiaOutputConverter
from ..models import Realty, RealtyDetails


class AbstractUpdater(ABC):
    """
    Abstract class for updaters
    """

    @abstractmethod
    def update_records(self):
        """
        Runs the logic to update all data
        """
        ...

    @abstractmethod
    def update_single_record(self, db_record: Row):
        """
        Runs the logic to update single ad
        :param db_record: Data from the database for comparison with new ones
        """
        ...

    @abstractmethod
    def rewrite(self, converter, realty_details):
        """
        Called if the information in the database does not match the last
        """
        ...

    @abstractmethod
    def update_to_non_actual(self, db_record: Row):
        """
        Called if the ad from the database does not exist on the server
        """
        ...


class RealtyUpdater(AbstractUpdater):
    """
    Domria realty updater
    """

    def __init__(self):
        self.metadata = open_metadata(PATH_TO_METADATA)["DOMRIA API"]
        with session_scope() as session:
            self.cursor = session.execute(
                "SELECT floor, floors_number, square, price, original_url FROM realty_details"
            )
        self.params = {"api_key": DomriaLimitationSystem.get_token()}
        for param, val in self.metadata["optional"].items():
            self.params[param] = val
        self.url = "{base_url}{condition}{single_ad}".format(
            base_url=self.metadata["base_url"],
            single_ad=self.metadata["urls"]["single_ad"]["url_prefix"],
            condition=self.metadata["urls"]["single_ad"]["condition"]
        )

    def update_records(self):
        """
        Runs the logic to update all data
        """
        for db_record in self.cursor:
            LOGGER.info(db_record)
            self.update_single_record(db_record)

    def send_request_by_id(self, ad_id: int):
        """
        Send request to get info about single ad by id
        """
        response = requests.get(self.url.format(id=ad_id),
                                params=self.params,
                                headers={'User-Agent': 'Mozilla/5.0'})

        if not response:
            raise ResponseNotOkException(response)

        return response.json()

    def is_actual(self, response: Dict):
        """
        Check to see if such an ad exists.
        If not, it is non actual and does not require updating
        """
        return response.get("priceArr", None)

    def update_single_record(self, db_record: Row):
        """
        Runs the logic to update single ad
        :param db_record: Data from the database for comparison with new ones
        """
        response = self.send_request_by_id(db_record.original_url[-13:-5])

        if not response:
            raise ResponseNotOkException(response)

        if not self.is_actual(response):
            self.update_to_non_actual(db_record)

        service_converter = DomRiaOutputConverter(response, self.metadata)
        try:
            realty_details = service_converter.make_realty_details_data()
        except json.JSONDecodeError:
            print("An error occurred while converting data from Dom Ria for realty_details model")
            raise
        new_realty = tuple(value for key, value in realty_details.items() if key != "published_at")

        if new_realty != db_record:
            self.update_to_non_actual(db_record)
            self.rewrite(service_converter, realty_details)

    def rewrite(self, converter: DomRiaOutputConverter, realty_details: Dict):
        """
        Create RealtyLoadersFactory and load new info about realty to database
        """
        try:
            realty_data = converter.make_realty_data()
        except json.JSONDecodeError:
            print("An error occurred while converting data from Dom Ria for realty model")
            raise

        try:
            load_data(schemas.RealtyDetailsSchema(), realty_details, models.RealtyDetails)
            load_data(schemas.RealtySchema(), realty_data, models.Realty)
        except MetaDataError as error:
            raise InternalServerErrorException() from error

    def update_to_non_actual(self, db_record: Row):
        """
        Called if the ad from the database does not exist on the server
        """
        with session_scope() as session:
            realty_details = session.query(RealtyDetails).filter(
                RealtyDetails.original_url == db_record[-1] and RealtyDetails.version is None
            ).first()
            realty = session.query(Realty).filter(Realty.id == realty_details.id).first()

            if realty:
                realty.version = datetime.datetime.utcnow()
                realty_details.version = datetime.datetime.utcnow()


if __name__ == "__main__":
    RealtyUpdater().update_records()
