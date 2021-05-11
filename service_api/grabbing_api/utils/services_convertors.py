"""
Output and input converters for DomRia service
"""
import datetime
import json
from abc import ABC, abstractmethod
from typing import Dict

import requests
from redis import RedisError

from service_api import CACHE, LOGGER, models, session_scope
from service_api.errors import BadRequestException
from service_api.exceptions import (BadFiltersException, MetaDataError, ObjectNotFoundException)
from service_api.grabbing_api.constants import (CACHED_CHARACTERISTICS, CACHED_CHARACTERISTICS_EXPIRE_TIME,
                                                DOMRIA_TOKEN, PATH_TO_METADATA, GE, LE)
from service_api.grabbing_api.utils.grabbing_utils import (open_metadata, recognize_by_alias)


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
            raise BadRequestException(error.args) from error

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


class DomRiaOutputConverter(AbstractOutputConverter):
    """
    A class for converting characteristics specified by the user into data to be sent to DomRia
    """

    def make_realty_details_data(self) -> Dict:
        """
        Composes data for RealtyDetails model
        """

        realty_details_meta = self.service_metadata["urls"]["single_ad"]["models"]["realty_details"]

        values = [self.response.get(val, None) for val in realty_details_meta["fields"].values()]

        realty_details_data = dict(zip(
            realty_details_meta["fields"].keys(), values
        ))

        return realty_details_data

    def make_realty_data(self) -> Dict:
        """
        Composes data for Realty model
        """
        realty_data = {}
        realty_meta = self.service_metadata["urls"]["single_ad"]["models"]["realty"]
        fields = realty_meta["fields"].copy()
        with session_scope() as session:

            service = session.query(models.Service).filter(
                models.Service.name == self.service_metadata["name"]
            ).first()

            if not service:
                raise Warning("There is no such service named {}".format(service))

            realty_data["service_id"] = service.id

            city_characteristics = fields.pop("city_id", None)

            for key, characteristics in fields.items():
                model = characteristics["model"]
                response_key = characteristics["response_key"]

                model = getattr(models, model)

                if not model:
                    raise Warning("There is no such model named {}".format(model))

                try:
                    obj = recognize_by_alias(model, self.response[response_key])
                except ObjectNotFoundException as error:
                    print(error.args)
                    break
                realty_data[key] = obj.id

            if city_characteristics:
                cities_by_state = session.query(models.City).filter_by(state_id=realty_data["state_id"])
                realty_data["city_id"] = recognize_by_alias(models.City,
                                                            self.response[city_characteristics["response_key"]],
                                                            cities_by_state).id

        return realty_data


class DomRiaInputConverter(AbstractInputConverter):
    """
    Class to convert response returned from DomRia to database-ready data
    """

    def convert(self):
        """
        Convert user params to send a request to the server
        """
        params = self.convert_named_field(self.realty)
        params.update(self.convert_characteristic_fields(self.characteristics))
        params["page"] = (self.additional["page"] // self.additional["page_ads_number"]) + 1
        return params

    def convert_characteristic_fields(self, characteristic_filters: Dict):
        """
        Convert domria params (characteristics) to number representation
        """
        with session_scope() as session:
            realty_type_aliases = session.query(models.RealtyType).get(self.realty["realty_type_id"]).aliases

        type_mapper = self.process_characteristics(realty_type_aliases, CACHED_CHARACTERISTICS_EXPIRE_TIME,
                                                   CACHED_CHARACTERISTICS)

        fields, filters = self.search_realty_metadata["models"]["realty_details"]["fields"], {}

        for key, value in characteristic_filters.items():
            service_key = fields[key]["response_key"]
            if service_key in type_mapper:
                filters[type_mapper[service_key]] = {"name": key, "values": value}

        characteristic_filters = self.build_new_dict(filters, self.search_realty_metadata["models"]["realty_details"])

        return characteristic_filters

    def convert_named_field(self, realty_filters: Dict):
        """
        Convert fields names to service names and replace id for its api
        """
        params = {}
        with session_scope() as session:

            realty_meta = self.search_realty_metadata["models"]["realty"]["fields"]

            for param, value in realty_filters.items():
                if param not in realty_meta:
                    continue

                model = realty_meta[param]["model"]
                model = getattr(models, model, None)

                if model is None:
                    raise MetaDataError(message="No model in {param} field of search for realty model")

                service = session.query(models.Service).filter_by(name=self.service_name).first()
                if service is None:
                    raise ObjectNotFoundException("Service with name: {} not found".format(self.service_name))

                xref_record = session.query(model).get({"entity_id": value, "service_id": service.id})

                params[realty_meta[param]["request_key"]] = xref_record.original_id

        return params

    def build_new_dict(self, params: dict, realty_details_metadata) -> dict:
        """
        Method, that forms dictionary with parameters for the request
        """
        new_params, fields_desc = {}, realty_details_metadata["fields"]
        for parameter, value in params.items():
            char_description = fields_desc[value["name"]]
            if char_description["eq"] is not None:
                key = char_description["eq"].format(value=str(parameter))
                new_params[key] = value
                continue

            value_from = value.get("values")[GE]
            value_to = value.get("values")[LE]

            key_from = char_description["ge"].format(value_from=str(parameter))
            key_to = char_description["le"].format(value_to=str(parameter))

            new_params[key_from] = value_from
            new_params[key_to] = value_to

        return new_params

    def process_characteristics(self, realty_type_aliases, redis_ex_time: Dict, redis_characteristics: str):
        """
        Retrieves data from Redis and converts it to the required format for the request
        """
        cached_characteristics = CACHE.get(redis_characteristics)
        if cached_characteristics is None:
            try:
                characteristics = DomriaCharacteristicLoader().load()
                CACHE.set(redis_characteristics,
                          json.dumps(characteristics),
                          datetime.timedelta(**redis_ex_time))
            except json.JSONDecodeError as error:
                raise json.JSONDecodeError from error
            except RedisError as error:
                raise RedisError(error.args) from error
        else:
            characteristics = json.loads(cached_characteristics)

        for alias in realty_type_aliases:
            if alias.alias in characteristics:
                realty_type_name = alias.alias
                break
        else:
            raise ObjectNotFoundException("Name for realty from aliases type not found")

        try:
            type_mapper = characteristics[realty_type_name]
        except KeyError as error:
            raise BadFiltersException("No such realty type name: {}".format(realty_type_name)) from error

        return type_mapper


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

        params = {"api_key": DOMRIA_TOKEN}

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
            req = requests.get(url=url, params=params, headers={'User-Agent': 'Mozilla/5.0'})

            requested_characteristics = req.json(object_hook=self.decode_characteristics)
            requested_characteristics = [
                element for element in requested_characteristics if element != {}
            ]

            named_characteristics = {}
            for character in requested_characteristics:
                named_characteristics.update(character)
            characteristics.update({element: named_characteristics})
        return characteristics
