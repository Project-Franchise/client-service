"""
Resources and urls for grabbing service
"""
import itertools
import pickle
import json

from contextlib import contextmanager
import datetime
from typing import List, Iterator

from flask import request
import requests
from flask_restful import Resource
from redis.exceptions import RedisError
from service_api import Session as Session_
from service_api import api_, models, schemas, CACHE
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .utils.grabbing_utils import process_request

from . import constants
from .characteristics import get_characteristics
from .realty_requests import RealtyRequestToDomria


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


class LatestDataFromDomriaResource(Resource):

    def post(self):
        params = request.get_json()

        print("CACHE")

        cached_characteristics = CACHE.get(constants.REDIS_CHARACTERISTICS)
        if cached_characteristics is None:
            try:
                # load new characteristics
                mapper = get_characteristics()
                CACHE.set(constants.REDIS_CHARACTERISTICS,
                          json.dumps(mapper),
                          datetime.timedelta(**constants.REDIS_CHARACTERISTICS_EX_TIME))
            except json.JSONDecodeError:
                return {"status": "failed",
                        "error_message": "json_error"}
            except RedisError:
                return {"status": "failed",
                        "erorr_message": "redis_error"}
        else:
            mapper = json.loads(cached_characteristics)

        # validation
        with session_scope() as session:
            realty_type = session.query(models.RealtyType).get(params.get("realty_type"))

        try:
            type_mapper = mapper.get(realty_type.name)

            page = params.pop("page")
            page_ads_number = params.pop("page_ads_number")
        except Exception:
            return {"error": "E"}
        
        # mapping text characteristics to theirs domria ids

        # CHANGE CITY ID TO ORINAL ID
        new_params = dict((type_mapper.get(key, key), value)
                          for key, value in params.items())

        # sending request for realty-ids list
        items = RealtyRequestToDomria().get(new_params)

        # getting realty serialized data and write them into db
        with session_scope() as session:
            realty_json = process_request(
                items, session, page, page_ads_number)

        return realty_json


# Be careful. Use this lisnks only once!!
api_.add_resource(StatesFromDomriaResource, "/grabbing/states")
api_.add_resource(CitiesFromDomriaResource, "/grabbing/cities")
api_.add_resource(LatestDataFromDomriaResource, "/grabbing/latest")
