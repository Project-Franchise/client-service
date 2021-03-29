"""
Resources and urls for grabbing service
"""
import itertools
import pickle

from contextlib import contextmanager
from typing import List, Iterator

import requests
from flask_restful import Resource
from redis.exceptions import RedisError
from ...service_api import CACHE
from service_api import Session as Session_
from service_api import api_, models, schemas
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from . import constants


@contextmanager
def session_scope() -> Iterator[Session]:
    session = Session_()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    else:
        try:
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise


class CitiesFromDomriaResource(Resource):
    """
    Retrieving cities from DOMRIA and saving to DB
    """

    def get(self):
        """
        Get all cities from all states
        :return: list of serialized cities
        """
        cached_sates_status = CACHE.get(constants.REDIS_STATES_FETCHED)
        if cached_sates_status is not None and \
           pickle.loads(cached_sates_status):

            city_schema = schemas.CitySchema(many=True)

            cached_status = CACHE.get(constants.REDIS_CITIES_FETCHED)
            if cached_status is not None and pickle.loads(cached_status):
                with session_scope() as session:
                    cities = session.query(models.City).all()

                return {
                    "status": "Allready in db",
                    "data": city_schema.dump(cities)
                }
            with session_scope() as session:
                states = session.query(models.State).all()

            with session_scope() as session:
                city_generator = (self.get_cities_by_state(state, city_schema)
                                  for state in states)
                cities = list(itertools.chain.from_iterable(city_generator))

                try:
                    CACHE.set(constants.REDIS_CITIES_FETCHED,
                              pickle.dumps(True))
                except RedisError:
                    session.rollback()
                    return {
                        "status": "redis failed",
                        "data": None
                    }

            return {
                "status": "fetched from domria",
                "data": cities
            }

        return {
            "status": "failed",
            "error_message": "There is no state in db"
        }

    @staticmethod
    def get_cities_by_state(state: models.State,
                            city_schema: schemas.Schema) -> List[dict]:
        """
        Getting cities from DOMRIA by original state id.
        Returns list of serialized cities
        :param: state: State
        :return: List[dict]
        """
        params = {
            "lang_id": constants.DOMRIA_UKR,
            "api_key": constants.DOMRIA_API_KEY
        }

        url = constants.DOMRIA_DOMAIN + \
            constants.DOMRIA_URL["cities"] + f"/{state.original_id}"
        response = requests.get(url, params=params)

        cities_json = response.json()

        try:
            processed_cities = [{"name": city["name"],
                                 "original_id": city["cityID"],
                                 "state_id": state.id}
                                for city in cities_json]
        except KeyError:
            return []

        cities = city_schema.load(processed_cities)

        with session_scope() as session:
            session.add_all(cities)

        return processed_cities

    def delete(self):
        """
        Drops all cities from DB
        and delete redis fetch value too
        """
        with session_scope as session:
            session.query(models.City).delete()
            CACHE.delete(constants.REDIS_CITIES_FETCHED)

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

        state_schema = schemas.StateSchema(many=True)

        cached_status = CACHE.get(constants.REDIS_STATES_FETCHED)
        if cached_status is not None and pickle.loads(cached_status):
            with session_scope() as session:
                states_from_db = session.query(models.State).all()
            return {
                "status": "Allready in db",
                "data": state_schema.dump(states_from_db)
            }

        params = {
            "lang_id": constants.DOMRIA_UKR,
            "api_key": constants.DOMRIA_API_KEY
        }
        response = requests.get(constants.DOMRIA_DOMAIN +
                                constants.DOMRIA_URL["states"], params=params)

        states_json = response.json()

        processed_states = [{"name": state["name"],
                             "original_id": state["stateID"]}
                            for state in states_json]

        states = state_schema.load(processed_states)

        with session_scope() as session:
            session.add_all(states)

        CACHE.set(constants.REDIS_STATES_FETCHED, pickle.dumps(True))

        return {
            "status": "fetched from domria",
            "data": processed_states
        }

    def delete(self):
        """
        Drops all states and cities from DB
        and delete redis fetch value for both
        """
        with session_scope as session:
            session.query(models.City).delete()
            session.query(models.State).delete()
            CACHE.delete(constants.REDIS_STATES_FETCHED)
            CACHE.delete(constants.REDIS_CITIES_FETCHED)

        return "SUCCESS"


class RequestToDomria():
    """
    Send requests for getting list of id of items
    """

    @staticmethod
    def form_new_dict(params: dict) -> dict:
        """
        Method, that forms dictionary with parameters for the request
        """
        new_params = dict()
        for parameters in params:
            if isinstance(parameters, int):
                if isinstance(params.get(parameters), dict):
                    new_key_from = 'characteristic%5B' + str(parameters) + '%5D%5Bfrom%5D'
                    new_value_from = params[parameters].get("from")
                    new_key_to = 'characteristic%5B' + str(parameters) + '%5D%5Bto%5D'
                    new_value_to = params[parameters].get("to")
                    new_params[new_key_from] = new_value_from
                    new_params[new_key_to] = new_value_to
                else:
                    new_key = 'characteristic%5B' + str(parameters) + '%5D'
                    new_value = params.get(parameters)
                    new_params[new_key] = new_value
            else:
                new_params[parameters] = params.get(parameters)
        return new_params

    def get(self, params: dict) -> dict:
        """
        Get all items from DOMRIA by parameters
        :return: Dict
        """

        params = {
            'category': 1,
            'realty_type': 2,
            'operation_type': 1,
            'state_id': 10,
            'city_id': 10,
            'district_id': [15187, 15189, 15188],
            209: {'from': 1, 'to': 3},
            214: {'from': 60, 'to': 90},
            216: {'from': 30, 'to': 50},
            218: {'from': 4, 'to': 9},
            227: {'from': 3, 'to': 7},
            443: 442,
            234: {'from': 20000, 'to': 90000},
            242: 239,
            273: 273,
            1437: 1434,
            'api_key': constants.DOMRIA_API_KEY,
        }

        new_params = self.form_new_dict(params)

        response = requests.get(constants.DOMRIA_DOMAIN +
                                constants.DOMRIA_URL["search"], params=new_params)

        items_json = response.json()
        return items_json


# Be careful. Use this links only once!!
api_.add_resource(StatesFromDomriaResource, "/get-states-from-domria")
api_.add_resource(CitiesFromDomriaResource, "/get-cities-from-domria")