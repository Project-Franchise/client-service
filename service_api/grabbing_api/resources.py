"""
Resources and urls for grabbing service
"""
import itertools
import pickle
from typing import List, Dict

import requests
from flask import request
from flask_restful import Resource
from redis.exceptions import RedisError

from service_api import CACHE, api_, session_scope, models
from service_api.constants import URLS
from service_api.errors import BadRequestException
from service_api.schemas import CitySchema, StateSchema
from service_api.grabbing_api.realty_requests import RealtyRequesterToServiceResource
from .characteristics import process_characteristics
from .constants import (REDIS_CHARACTERISTICS,
                        REDIS_CHARACTERISTICS_EX_TIME, REDIS_CITIES_FETCHED,
                        REDIS_STATES_FETCHED, PATH_TO_METADATA)
from .utils.grabbing_utils import process_request, open_metadata, load_data


class CitiesFromDomriaResource(Resource):
    """
    Retrieving cities from DOMRIA and saving to DB
    """

    def get(self):
        """
        Get all cities from all states
        :return: list of serialized cities
        """
        cached_sates_status = CACHE.get(REDIS_STATES_FETCHED)
        if cached_sates_status is not None and pickle.loads(cached_sates_status):

            city_schema = CitySchema(many=True)

            cached_status = CACHE.get(REDIS_CITIES_FETCHED)
            if cached_status is not None and pickle.loads(cached_status):
                with session_scope() as session:
                    cities = session.query(models.City).all()

                return {
                    "status": "Already in db",
                    "data": city_schema.dump(cities)
                }

            with session_scope() as session:
                states = session.query(models.State).all()

            city_generator = (self.get_cities_by_state(state) for state in states)
            cities = list(itertools.chain.from_iterable(city_generator))

            try:
                CACHE.set(REDIS_CITIES_FETCHED, pickle.dumps(True))
            except RedisError as error:
                raise RedisError from error

            return {
                "status": "fetched from domria",
                "data": cities
            }

        raise BadRequestException("There is no state in db")

    @staticmethod
    def get_cities_by_state(state: models.State) -> List[dict]:
        """
        Getting cities from DOMRIA by original state id.
        Returns list of serialized cities
        :param: state: State
        :return: List[dict]
        """

        metadata = open_metadata(PATH_TO_METADATA)

        processed_cities = []
        for service_name in metadata:
            service_metadata = metadata[service_name]
            params = {}
            for param, val in service_metadata["optional"].items():
                params[param] = val

            url = "{base_url}{cities}{condition}{original_id}".format(
                base_url=service_metadata["base_url"],
                cities=service_metadata["url_rules"]["cities"]["url_prefix"],
                condition=service_metadata["url_rules"]["cities"]["condition"],
                original_id=state.original_id
            )
            response = requests.get(url=url, params=params, headers={'User-Agent': 'Mozilla/5.0'})

            try:
                service_cities = [{"name": city["name"],
                                   "original_id": city["cityID"],
                                   "state_id": state.id}
                                  for city in response.json()]  # service = service_name if name in db
                processed_cities += service_cities
            except KeyError:
                return []

            load_data(service_cities, models.City, CitySchema)
            # try:
            #     valid_data = CitySchema(many=True).load(service_cities)
            #     cities = [models.City(**valid_city) for valid_city in valid_data]
            # except ValidationError as error:
            #     raise BadRequestException(error.args) from error
            #
            # with session_scope() as session:
            #     session.add_all(cities)

        return processed_cities

    def delete(self):
        """
        Drops all cities from DB
        and delete redis fetch value too
        """
        with session_scope() as session:
            session.query(models.City).delete()
            CACHE.delete(REDIS_CITIES_FETCHED)

        return "SUCCESS"


class StatesFromDomriaResource(Resource):
    """
    Retrieving states from DOMRIA and saving to DB
    """

    def get(self):
        """
        Get all states from all states
        :return: list of serialized states
        """

        state_schema = StateSchema(many=True)

        cached_status = CACHE.get(REDIS_STATES_FETCHED)
        if cached_status is not None and pickle.loads(cached_status):
            with session_scope() as session:
                states_from_db = session.query(models.State).all()
            return {
                "status": "Already in db",
                "data": state_schema.dump(states_from_db)
            }

        metadata = open_metadata(PATH_TO_METADATA)
        processed_states = []
        for service_name in metadata:
            service_metadata = metadata[service_name]
            params = {}
            for param, val in service_metadata["optional"].items():
                params[param] = val

            url = "{base_url}{states}".format(
                base_url=service_metadata["base_url"],
                states=service_metadata["url_rules"]["states"]["url_prefix"],
            )

            response = requests.get(url=url, params=params, headers={'User-Agent': 'Mozilla/5.0'})

            try:
                service_states = [{"name": state["name"],
                                   "original_id": state["stateID"]}
                                  for state in response.json()]
                processed_states += service_states
            except KeyError:
                return []

            load_data(service_states, models.State, StateSchema)
            # try:
            #     valid_data = StateSchema(many=True).load(service_states)
            #     states = [models.State(**valid_state) for valid_state in valid_data]
            # except ValidationError as error:
            #     raise BadRequestException(error.args) from error
            #
            # with session_scope() as session:
            #     session.add_all(states)

            CACHE.set(REDIS_STATES_FETCHED, pickle.dumps(True))

        return {
            "status": "fetched from domria",
            "data": processed_states
        }

    def delete(self):
        """
        Drops all states and cities from DB
        and delete redis fetch value for both
        """
        with session_scope() as session:
            session.query(models.City).delete()
            session.query(models.State).delete()
            CACHE.delete(REDIS_STATES_FETCHED)
            CACHE.delete(REDIS_CITIES_FETCHED)

        return "SUCCESS"


class LatestDataResource(Resource):
    """
    Resource that is responsible for manipulation with latest data from resources described on metadata
    """

    @staticmethod
    def convert_named_filed(realty: Dict, service_metadata: Dict):
        """
        Convert fields names to service names and replace id for its api
        """
        params = {}
        with session_scope() as session:
            for param, characteristics in service_metadata["realty_columns"].items():
                if not characteristics["request_key"]:
                    continue

                model = characteristics["model"]
                service_param = characteristics["request_key"]

                model = getattr(models, model)
                if not model:
                    raise Warning(f"There is no such model named {model}")

                if param in realty:
                    obj = session.query(model).get(realty[param])
                    if obj is None:
                        raise BadRequestException("No such filters!")
                    params[service_param] = obj.original_id
        return params

    def post(self):
        """
        Returns latest information about realty and save it to DB
        """

        post_body = request.get_json()

        try:
            characteristics = post_body["characteristics"]
            realty = post_body["realty_filters"]
            additional = post_body["additional"]
        except KeyError as error:
            raise BadRequestException(error.args) from error

        metadata = open_metadata(PATH_TO_METADATA)

        for service_name in metadata:
            service_metadata = metadata[service_name]
            params = self.convert_named_filed(realty, service_metadata)

            type_mapper = process_characteristics(service_metadata, realty, REDIS_CHARACTERISTICS_EX_TIME,
                                                  REDIS_CHARACTERISTICS)
            params.update(dict((type_mapper.get(key, key), {"name": key, "values": value})
                               for key, value in characteristics.items()))

            items = RealtyRequesterToServiceResource().get(params, service_metadata)
            try:
                return process_request(items, dict(additional).pop("page"), additional.pop("page_ads_number"),
                                       service_metadata)
            except KeyError as error:
                print(error.args)
                raise BadRequestException(error.args) from error


# Be careful. Use this links only once!!
api_.add_resource(StatesFromDomriaResource, URLS["GRABBING"]["GET_STATES_URL"])
api_.add_resource(CitiesFromDomriaResource, URLS["GRABBING"]["GET_CITIES_URL"])
api_.add_resource(LatestDataResource, URLS["GRABBING"]["GET_LATEST_URL"])
