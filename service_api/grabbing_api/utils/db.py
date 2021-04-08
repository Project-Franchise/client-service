from abc import ABC, abstractmethod
import requests
from service_api.schemas import CitySchema
from service_api.models import City, State
from marshmallow.exceptions import ValidationError
from service_api.errors import BadRequestException
from service_api import session_scope, CACHE
from typing import List, Dict, Any
from service_api.grabbing_api.constants import REDIS_CITIES_FETCHED, REDIS_STATES_FETCHED
import pickle
import json
import itertools

class BaseLoader(ABC):
    """
    Abstract class for loading static base date to DB (exmp. cities, states, realty_types...)
    """

    @abstractmethod
    @property
    def name(self):
        """
        Name of this class
        Is used in metadata
        """
        pass

    @abstractmethod
    def load_to_db(self) -> None:
        """
        Main function of retrieving and loading data to db
        """
        pass



class LoadCitiesToDB(BaseLoader):
    __name = "cities_loader"

    @property
    def name(self):
        return self.__name

    def load_to_db(self) -> Dict:
        """
        Get all cities from all states
        :return: list of serialized cities
        """
        cached_sates_status = CACHE.get(REDIS_STATES_FETCHED)
        with session_scope() as session:
            number_of_cities_by_state = session.query(City).group_by(City.state_id).order_by(City.state_id).count()

        if cached_sates_status is not None and \
           json.loads(cached_sates_status) == number_of_cities_by_state:

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
                states = session.query(State).order_by(State.id).all()

            for cities_by_state in (self.__get_cities_by_state(state) for state in states):

            cities = list(itertools.chain.from_iterable(city_generator))


            try:
                CACHE.set(REDIS_CITIES_FETCHED, json.dumps(True))
            except RedisError as error:
                raise RedisError(error.args)

            return {
                "status": "fetched from domria",
                "data": cities
            }

        raise BadRequestException("There is no state in db")

    def __get_cities_by_state(self, state) -> List[Dict[str, Any]]:
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
        except ValidationError:
            raise BadRequestException("Validation failed")

        with session_scope() as session:
            session.add_all(cities)

        return processed_cities
