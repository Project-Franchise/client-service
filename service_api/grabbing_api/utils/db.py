"""
Module with data Loaders
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests
from marshmallow.exceptions import ValidationError
from requests.exceptions import RequestException
from service_api import session_scope
from service_api.exceptions import ObjectNotFound, ResponseNotOk
from service_api.grabbing_api.constants import DOMRIA_TOKEN, PATH_TO_METADATA
from service_api.models import City, OperationType, RealtyType, State
from service_api.schemas import (CitySchema, OperationTypeSchema,
                                 RealtyTypeSchema, StateSchema)

from .grabbing_utils import load_data, open_metadata


class BaseLoader(ABC):
    """
    Abstract class for loading static base date to DB (exmp. cities, states, realty_types...)
    """

    @abstractmethod
    def load_to_db(self, *args, **kwargs) -> None:
        """
        Main function of retrieving and loading data to db
        """
        return None


class CityLoader(BaseLoader):
    """
    Loads cities to db
    """

    def load_to_db(self, *args, **kwargs) -> Dict[int, int]:
        state_ids: List[int] = args[0]
        print(state_ids)
        return {state_id: self.load_cities_by_state(state_id=state_id) for state_id in state_ids}

    def load_cities_by_state(self, **kwargs: int) -> int:
        """
        Getting cities from DOMRIA by original state_id
        Returns amount of fetched cities
        :param: state_id: int
        :return: int
        """

        if (state_id := kwargs.get("state_id")) is None:
            raise KeyError("No parameter state_id provided in function load_to_db")

        with session_scope() as session:
            state = session.query(State).get({"id": state_id})

        if state is None:
            raise ObjectNotFound(errors=["No such state_id in DB"])

        domria_meta = open_metadata(PATH_TO_METADATA)["DOMRIA API"]
        domria_cities_meta = domria_meta["url_rules"]["cities"]

        params = {
            "lang_id": domria_meta["optional"]["lang_id"],
            "api_key": DOMRIA_TOKEN
        }

        response = requests.get("{}{}/{}".format(domria_meta["base_url"],
                                                 domria_cities_meta["url_prefix"],
                                                 state.original_id),
                                params=params)
        if not response.ok:
            raise ResponseNotOk(response.text)

        processed_cities = []
        for city in response.json():
            processed_city = {key: city[external_service_key]
                              for key, external_service_key in domria_cities_meta["filters"].items()}
            processed_city["state_id"] = state.id
            processed_cities.append(processed_city)

        for data in processed_cities:
            try:
                load_data(data, City, CitySchema)
            except ValidationError as error:
                print(error)
                raise

        return len(processed_cities)


class StateLoader(BaseLoader):
    """
    Loads sates to db
    """

    def load_to_db(self, *args, **kwargs) -> int:
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

    def load_to_db(self, *args, **kwargs) -> int:
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


class OperationTypeLoader(BaseLoader):
    """
    Loads OperationType from metadata
    """

    def load_to_db(self, *args, **kwargs) -> int:
        """
        Getting operation types from metadata
        Returns amount of fetched operation types
        :return: int
        """

        domria_meta = open_metadata(PATH_TO_METADATA)["DOMRIA API"]
        operation_types = domria_meta["url_characteristics"]["operation_type"]

        keys = domria_meta["model_characteristics"]["operation_type"]["filters"].keys()

        for operation_type_name, operation_type_original_id in operation_types.items():
            data = dict(zip(keys, (operation_type_name, operation_type_original_id)))
            load_data(data, OperationType, OperationTypeSchema)

        return len(operation_types)


class LoadersFactory:
    """
    Load core data to db based on str input
    """
    __mapper: dict[str, BaseLoader] = {
        "cities": CityLoader,
        "states": StateLoader,
        "realty_types": RealtyTypeLoader,
        "operation_types": OperationTypeLoader
    }

    def get_available_entites(self) -> List[str]:
        """
        Returns all possible name of entities stored in mapper
        :return: list[str] with name of entities
        """
        return self.__mapper.keys()

    def load(self, **entities_to_load: List) -> Dict[str, Any]:
        """
        Calls mapped loader clasees for keys in params dict input
        :params: dict[str, List] str - name of entity to load (func get_available_entites)
                                 List - args for Loader classes
        :return: dict[str, Any] str - name of entities from input
                                Any - json-like status info about fetching data to db
        """

        statuses = {}
        for entity, values in entities_to_load.items():
            try:
                statuses[entity] = {"status": "SUCCESSFUL", "data": self.__mapper[entity]().load_to_db(values)}
            except ObjectNotFound as error:
                error_mesaage = error.errors
            except ResponseNotOk as error:
                error_mesaage = error.args
            except KeyError as error:
                error_mesaage = error.args
            except ValidationError as error:
                error_mesaage = error.messages
            else:
                continue
            print(error_mesaage)
            statuses[entity] = {"status": "FAILED", "data": error_mesaage}

        return statuses
