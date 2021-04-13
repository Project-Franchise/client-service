"""
Module with data Loaders
"""
from abc import ABC, abstractmethod

import requests
from requests.exceptions import RequestException
from service_api import session_scope
from service_api.grabbing_api.constants import DOMRIA_TOKEN, PATH_TO_METADATA
from service_api.models import City, RealtyType, State
from service_api.schemas import CitySchema, RealtyTypeSchema, StateSchema

from .grabbing_utils import load_data, open_metadata


class BaseLoader(ABC):
    """
    Abstract class for loading static base date to DB (exmp. cities, states, realty_types...)
    """

    @abstractmethod
    def load_to_db(self, **kwargs) -> None:
        """
        Main function of retrieving and loading data to db
        """
        return None


class CityLoader(BaseLoader):
    """
    Loads cities to db
    """

    def load_to_db(self, **kwargs) -> int:
        """
        Getting cities from DOMRIA by original state_id
        Returns amount of fetched cities
        :param: state_id: int
        :return: int
        """

        if state_id := kwargs.get("state_id"):
            raise KeyError("No parameter state_id provided in function load_to_db")

        with session_scope() as session:
            state = session.query(State).get({"id": state_id})

        domria_meta = open_metadata(PATH_TO_METADATA)["DOMRIA API"]
        domria_cities_meta = domria_meta["url_rules"]["cities"]

        params = {
            "lang_id": domria_meta["optional"]["lang_id"],
            "api_key": DOMRIA_TOKEN
        }

        url = "{}{}/{}".format(domria_meta["base_url"], domria_cities_meta["url_prefix"], state.original_id)
        response = requests.get(url, params=params)
        if not response.ok:
            raise RequestException(response.text)
        cities_json = response.json()

        processed_cities = []
        for city in cities_json:
            processed_city = {key: city[external_service_key]
                              for key, external_service_key in domria_cities_meta["filters"].items()}
            processed_city["state_id"] = state.id
            processed_cities.append(processed_city)

        for data in processed_cities:
            load_data(data, City, CitySchema)

        return len(processed_cities)


class StateLoader(BaseLoader):
    """
    Loads sates to db
    """

    def load_to_db(self, **kwargs) -> int:
        """
        Getting states from DOMRIA
        Returns amount of fetched states
        :return: int
        """

        domria_meta = open_metadata(PATH_TO_METADATA)["DOMRIA API"]
        domria_states_meta = domria_meta["url_rules"]["states"]

        params = {
            "lang_id": domria_meta["optional"]["lang_id"],
            "api_key": DOMRIA_TOKEN
        }

        url = "{}{}".format(domria_meta["base_url"], domria_states_meta["url_prefix"])
        response = requests.get(url, params=params)
        if not response.ok:
            raise RequestException(response.text)

        states_json = response.json()
        processed_states = [{key: state[external_service_key]
                             for key, external_service_key in domria_states_meta["filters"].items()}
                            for state in states_json]

        for data in processed_states:
            load_data(data, State, StateSchema)

        return len(processed_states)

class RealtyTypeLoader(BaseLoader):
    """
    Loads RealtyType from metadata
    """

    def load_to_db(self, **kwargs) -> int:
        """
        Getting realty types from metadata
        Returns amount of fetched realty types
        :return: int
        """
        domria_meta = open_metadata(PATH_TO_METADATA)["DOMRIA API"]
        realty_types = domria_meta["url_characteristics"]["realty_type"]

        keys = domria_meta["model_characteristics"]["realty_type"]["filters"].keys()

        for realty_type_name, realty_type_original_id in realty_types.items():
            data = dict(zip(keys, (realty_type_name, realty_type_original_id)))
            load_data(data, RealtyType, RealtyTypeSchema)

        return len(realty_types)
