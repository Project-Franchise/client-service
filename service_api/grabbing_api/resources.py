"""
Resources and urls for grabbing service
"""
import os
from typing import List

import requests
from flask_restful import Resource
from service_api import Session as Session_
from service_api import api_, models, schemas
from sqlalchemy.orm import Session

from . import constants


class CitiesFromDomriaResource(Resource):
    """
    Retrieving cities from DOMRIA and saving to DB
    """

    def get(self):
        """
        Get all cities from all states
        :return: list of serialized cities
        """
        session: Session = Session_()
        states = session.query(models.State).all()

        return [self.get_cities_by_state(state) for state in states]

    @staticmethod
    def get_cities_by_state(state: models.State) -> List[dict]:
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
            constants.DOMRIA_URL["cities"] + f'/{state.original_id}'
        response = requests.get(url, params=params)

        cities_json = response.json()
        city_schema = schemas.CitySchema(many=True)

        processed_cities = [{"name": city["name"],
                             "original_id": city["cityID"],
                             "state_id": state.id}
                            for city in cities_json]

        cities = city_schema.load(processed_cities)

        session: Session = Session_()
        session.add_all(cities)
        session.commit()

        return processed_cities


class StatesFromDomriaResource(Resource):
    """
    Retrieving states from DOMRIA and saving to DB
    """

    def get(self):
        """
        Get all states from all states
        :return: list of serialized cities
        """
        params = {
            "lang_id": constants.DOMRIA_UKR,
            "api_key": constants.DOMRIA_API_KEY
        }
        response = requests.get(constants.DOMRIA_DOMAIN +
                                constants.DOMRIA_URL["states"], params=params)

        states_json = response.json()
        state_schema = schemas.StateSchema(many=True)

        processed_states = [{"name": state["name"],
                             "original_id": state["stateID"]}
                            for state in states_json]

        states = state_schema.load(processed_states)

        session: Session = Session_()
        session.add_all(states)
        session.commit()

        return processed_states


# Be careful. Use this lisnks only once!!
api_.add_resource(StatesFromDomriaResource, "/get/states")
api_.add_resource(CitiesFromDomriaResource, "/get/cities")
