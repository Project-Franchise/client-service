"""
Module with data Loaders
"""
from abc import ABC, abstractmethod

import requests
from requests.exceptions import RequestException
from service_api import session_scope
from service_api.grabbing_api.constants import DOMRIA_TOKEN, PATH_TO_METADATA
from service_api.models import City, State
from service_api.schemas import CitySchema

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
