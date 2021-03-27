from flask_restful import Resource
import requests
import os
from service_api import api_, schemas, models, Session as Session_
from . import constants
from sqlalchemy.orm import Session


# ATENTION! THIS CODE SHOULD BE REFACRORED
# MADE WITH AIM TO PREVENT BLOCKING TASK #32


def get_cities(state):
    params = {
        "lang_id": 4,
        "api_key": os.environ['DOMRIA_API_KEY']
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


class CitiesFromDomriaResource(Resource):
    def get(self):
        session: Session = Session_()

        states = session.query(models.State).all()

        return [get_cities(state) for state in states]


class StatesFromDomriaResource(Resource):
    def get(self):
        params = {
            "lang_id": 4,
            "api_key": os.environ['DOMRIA_API_KEY']
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
