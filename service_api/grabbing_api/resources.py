"""
Resources and urls for grabbing service
"""
import datetime
import itertools
import json
import pickle
from typing import List

import requests
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from redis.exceptions import RedisError
from service_api import CACHE, api_, session_scope
from service_api.constants import URLS
from service_api.errors import BadRequestException
from service_api.models import City, RealtyType, State
from service_api.schemas import CitySchema, StateSchema

from .characteristics import get_characteristics
from .constants import (DOMRIA_API_KEY, DOMRIA_DOMAIN, DOMRIA_UKR, DOMRIA_URL,
                        REALTY_KEYS_FOR_REQUEST, REDIS_CHARACTERISTICS,
                        REDIS_CHARACTERISTICS_EX_TIME, REDIS_CITIES_FETCHED,
                        REDIS_STATES_FETCHED)
from .realty_requests import RealtyRequesterToDomria
from .utils.grabbing_utils import process_request


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
        if cached_sates_status is not None and \
           pickle.loads(cached_sates_status):

            city_schema = CitySchema(many=True)

            cached_status = CACHE.get(REDIS_CITIES_FETCHED)
            if cached_status is not None and pickle.loads(cached_status):
                with session_scope() as session:
                    cities = session.query(City).all()

                return {
                    "status": "Allready in db",
                    "data": city_schema.dump(cities)
                }

            with session_scope() as session:
                states = session.query(State).all()

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
    def get_cities_by_state(state: State) -> List[dict]:
        """
        Getting cities from DOMRIA by original state id.
        Returns list of serialized cities
        :param: state: State
        :return: List[dict]
        """
        params = {
            "lang_id": DOMRIA_UKR,
            "api_key": DOMRIA_API_KEY
        }

        url = DOMRIA_DOMAIN + \
            DOMRIA_URL["cities"] + f"/{state.original_id}"
        response = requests.get(url, params=params)

        cities_json = response.json()

        try:
            processed_cities = [{"name": city["name"],
                                 "original_id": city["cityID"],
                                 "state_id": state.id}
                                for city in cities_json]
        except KeyError:
            return []

        try:
            valid_data = CitySchema(many=True).load(processed_cities)
            cities = [City(**valid_city) for valid_city in valid_data]
        except ValidationError as error:
            raise BadRequestException(error.args) from error

        with session_scope() as session:
            session.add_all(cities)

        return processed_cities

    def delete(self):
        """
        Drops all cities from DB
        and delete redis fetch value too
        """
        with session_scope() as session:
            session.query(City).delete()
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
                states_from_db = session.query(State).all()
            return {
                "status": "Allready in db",
                "data": state_schema.dump(states_from_db)
            }

        params = {
            "lang_id": DOMRIA_UKR,
            "api_key": DOMRIA_API_KEY
        }
        response = requests.get(
            DOMRIA_DOMAIN + DOMRIA_URL["states"], params=params)

        states_json = response.json()

        processed_states = [{"name": state["name"],
                             "original_id": state["stateID"]}
                            for state in states_json]

        try:
            valid_data = StateSchema(many=True).load(processed_states)
            states = [State(**valid_state) for valid_state in valid_data]
        except ValidationError as error:
            raise BadRequestException(error.args) from error

        with session_scope() as session:
            session.add_all(states)

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
            session.query(City).delete()
            session.query(State).delete()
            CACHE.delete(REDIS_STATES_FETCHED)
            CACHE.delete(REDIS_CITIES_FETCHED)

        return "SUCCESS"


class LatestDataFromDomriaResource(Resource):
    """
    Resource that is responsible for manipulation with latest data from resources described on metadata
    """

    @staticmethod
    def named_filed_converter(realty):
        """
        Convert fileds names to domria names and replace id for its domria api
        """
        params = dict()
        with session_scope() as session:
            for param, model, domria_param in REALTY_KEYS_FOR_REQUEST:
                if param in realty:
                    obj = session.query(model).get(realty[param])
                    if obj is None:
                        raise BadRequestException("No such filters!")
                    params[domria_param] = obj.original_id

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
            raise BadRequestException(error.args)from error

        params = self.named_filed_converter(realty)

        cached_characteristics = CACHE.get(REDIS_CHARACTERISTICS)
        if cached_characteristics is None:
            try:
                mapper = get_characteristics()
                CACHE.set(REDIS_CHARACTERISTICS,
                          json.dumps(mapper),
                          datetime.timedelta(**REDIS_CHARACTERISTICS_EX_TIME))
            except json.JSONDecodeError as error:
                raise json.JSONDecodeError from error
            except RedisError as error:
                raise RedisError(error.args) from error
        else:
            mapper = json.loads(cached_characteristics)

        with session_scope() as session:
            realty_type = session.query(RealtyType).get(
                realty.get("realty_type_id"))

        if realty_type is None:
            raise BadRequestException("Invalid realty_type while getting latest data")

        try:
            type_mapper = mapper.get(realty_type.name)
        except Exception as error:
            print(error)
            raise

        params.update(dict((type_mapper.get(key, key), value)
                          for key, value in characteristics.items()))

        items = RealtyRequesterToDomria().get(params)
        with session_scope() as session:
            try:
                return process_request(items, dict(additional).pop("page"), additional.pop("page_ads_number"))
            except KeyError as error:
                print(error.args)
                raise BadRequestException(error.args) from error


# Be careful. Use this links only once!!
api_.add_resource(StatesFromDomriaResource, URLS["GRABBING"]["GET_STATES_URL"])
api_.add_resource(CitiesFromDomriaResource, URLS["GRABBING"]["GET_CITIES_URL"])
api_.add_resource(LatestDataFromDomriaResource, URLS["GRABBING"]["GET_LATEST_URL"])
