"""
Output and input converters for DomRia service
"""
import datetime
import json
from typing import Dict

from redis import RedisError
from service_api import CACHE, LOGGER, models, session_scope
from ...exceptions import (BadFiltersException, MetaDataError, ObjectNotFoundException)
from ...constants import (CACHED_CHARACTERISTICS, CACHED_CHARACTERISTICS_EXPIRE_TIME)

from ...utils import recognize_by_alias
from ..interfaces import AbstractInputConverter, AbstractOutputConverter
from .utils import DomriaCharacteristicLoader


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
        try:
            realty_details_data["original_url"] = \
                f"{self.service_metadata['pretty_url']}/{realty_details_data['original_url']}"
        except KeyError as error:
            raise MetaDataError("No such key in metadata: base_url or original_url") from error

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
                    raise ObjectNotFoundException("There is no such model named {}".format(model))

                try:
                    obj = recognize_by_alias(model, self.response[response_key])
                except ObjectNotFoundException as error:
                    LOGGER.error("%s, advertisement_id: %s", error.args, self.response.get("realty_id"))
                    raise
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
            if (value.get("values")).get("ge"):
                value_from = value.get("values")["ge"]
                key_from = char_description["ge"].format(value_from=str(parameter))
                new_params[key_from] = value_from
            if (value.get("values")).get("le"):
                value_to = value.get("values")["le"]
                key_to = char_description["le"].format(value_to=str(parameter))
                new_params[key_to] = value_to
        new_params["lang_id"] = 4
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
