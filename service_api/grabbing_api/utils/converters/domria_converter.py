"""
Output and input converters for DomRia service
"""
import datetime
import json
from abc import ABC, abstractmethod
from typing import Dict

import requests
from redis import RedisError

from service_api import models, session_scope, CACHE
from service_api.errors import BadRequestException
from service_api.grabbing_api.constants import CACHED_CHARACTERISTICS, CACHED_CHARACTERISTICS_EXPIRE_TIME, \
    DOMRIA_TOKEN, GE, LE


class AbstractInputConverter(ABC):
    """
    Abstract class for input converters
    """
    def __init__(self, post_body: Dict, service_metadata: Dict):
        """
        Sets self values and except parsing errors
        """
        self.metadata = service_metadata
        try:
            self.characteristics = post_body["characteristics"]
            self.realty = post_body["realty_filters"]
            self.additional = post_body["additional"]
        except KeyError as error:
            raise BadRequestException(error.args) from error

    @abstractmethod
    def convert(self):
        """
        Get all items from service by parameters
        :return: str
        :return: Dict
        """

    @abstractmethod
    def get_url(self, params: Dict) -> Dict:
        """
        Prepares params to send a request to the server
        """


class AbstractOutputConverter(ABC):
    """
    Abstract class for output converters
    """

    def __init__(self, response: requests.models.Response, service_metadata: Dict):
        """
        Sets self values
        """
        self.response = response.json()
        self.metadata = service_metadata

    @abstractmethod
    def make_realty_data(self):
        """
        Converts a response to a dictionary ready for writing realty in the database
        """

    @abstractmethod
    def make_realty_details_data(self):
        """
        Converts a response to a dictionary ready for writing realty_details in the database
        """


class DomRiaOutputConverter(AbstractOutputConverter):
    """
    A class for converting characteristics specified by the user into data to be sent to DomRia
    """

    def make_realty_details_data(self) -> Dict:
        """
        Composes data for RealtyDetails model
        """

        realty_details_meta = self.metadata["model_characteristics"]["realty_details_columns"]
        values = [self.response.get(val["response_key"], None) for val in realty_details_meta.values()]

        realty_details_data = dict(zip(
            realty_details_meta.keys(), values
        ))

        return realty_details_data

    def make_realty_data(self) -> Dict:
        """
        Composes data for Realty model
        """
        realty_data = {}
        realty_meta = self.metadata["model_characteristics"]["realty_columns"]

        with session_scope() as session:
            for key, characteristics in realty_meta.items():
                model = characteristics["model"]
                response_key = characteristics["response_key"]

                model = getattr(models, model)
                if not model:
                    raise Warning(f"There is no such model named {model}")

                realty_data[key] = (session.query(model).filter(
                    model.original_id == self.response[response_key]
                ).first()).id  # and service_name == service_name

        return realty_data


class DomRiaInputConverter(AbstractInputConverter):
    """
    Class to convert response returned from DomRia to database-ready data
    """

    def convert(self):
        """
        Convert user params to send a request to the server
        """
        params = self.convert_named_filed()

        type_mapper = self.process_characteristics(CACHED_CHARACTERISTICS_EXPIRE_TIME, CACHED_CHARACTERISTICS)
        params.update(dict((type_mapper.get(key, key), {"name": key, "values": value})
                           for key, value in self.characteristics.items()))
        params["page"] = (self.additional["page"] // self.additional["page_ads_number"]) + 1

        url, params = self.get_url(params)
        return url, params

    def convert_named_filed(self):
        """
        Convert fields names to service names and replace id for its api
        """
        params = {}
        with session_scope() as session:
            for param, characteristics in self.metadata["model_characteristics"]["realty_columns"].items():
                if not characteristics["request_key"]:
                    continue

                model = characteristics["model"]
                service_param = characteristics["request_key"]

                model = getattr(models, model)
                if not model:
                    raise Warning(f"There is no such model named {model}")

                if param in self.realty:
                    obj = session.query(model).get(self.realty[param])
                    if obj is None:
                        raise BadRequestException("No such filters!")
                    params[service_param] = obj.original_id  # change to aliases logic
        return params

    def get_url(self, params: Dict) -> tuple[str, dict]:
        """
        Get all items from DOMRIA by parameters
        :return: str
        :return: Dict
        """
        new_params = self.build_new_dict(params)

        new_params["api_key"] = DOMRIA_TOKEN  # RESOURCE_ID
        url = "{base_url}{search}".format(
            base_url=self.metadata["base_url"],
            search=self.metadata["url_rules"]["search"]["url_prefix"],
        )

        return url, new_params

    def build_new_dict(self, params: dict) -> dict:
        """
        Method, that forms dictionary with parameters for the request
        ::
        """
        new_params = {}
        for parameter, value in params.items():
            if isinstance(parameter, int):
                char_description = self.metadata["model_characteristics"]["realty_details_columns"]
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

    def get_characteristics(self, characteristics: Dict = None) -> Dict:
        """
        Function to get characteristics
        and retrieve them in dict
        """

        if characteristics is None:
            characteristics = {}

        characteristics_data_set = self.metadata["url_characteristics"]

        params = {"api_key": DOMRIA_TOKEN}
        for param, val in self.metadata["optional"].items():
            params[param] = val
        params["operation_type"] = 1

        for element in characteristics_data_set["realty_type"]:
            url = "{base_url}{options}".format(
                base_url=self.metadata["base_url"],
                options=self.metadata["url_rules"]["options"]["url_prefix"]
            )

            params["realty_type"] = characteristics_data_set["realty_type"][element]
            req = requests.get(
                url=url,
                params=params,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            requested_characteristics = req.json(object_hook=self.decode_characteristics)
            requested_characteristics = [
                element for element in requested_characteristics if element != {}
            ]

            named_characteristics = {}
            for character in requested_characteristics:
                named_characteristics.update(character)
            characteristics.update({element: named_characteristics})
        return characteristics

    def process_characteristics(self, redis_ex_time: Dict, redis_characteristics: str):
        """
        Retrieves data from Redis and converts it to the required format for the request
        """
        cached_characteristics = CACHE.get(redis_characteristics)
        if cached_characteristics is None:
            try:
                characteristics = self.get_characteristics()
                CACHE.set(redis_characteristics,
                          json.dumps(characteristics),
                          datetime.timedelta(**redis_ex_time))
            except json.JSONDecodeError as error:
                raise json.JSONDecodeError from error
            except RedisError as error:
                raise RedisError(error.args) from error
        else:
            characteristics = json.loads(cached_characteristics)

        with session_scope() as session:
            realty_type = session.query(models.RealtyType).get(
                self.realty.get("realty_type_id"))

        if realty_type is None:
            raise BadRequestException("Invalid realty_type while getting latest data")

        try:
            type_mapper = characteristics.get(realty_type.name)
        except Exception as error:
            print(error)
            raise

        return type_mapper
