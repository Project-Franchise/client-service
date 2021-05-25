"""
Domria loaders
"""

from typing import Dict, List

from marshmallow.exceptions import ValidationError
from requests.exceptions import RequestException
from sqlalchemy import select

from service_api import LOGGER, session_scope
from service_api.constants import VERSION_DEFAULT_TIMESTAMP
from service_api.exceptions import (AlreadyInDbException, ModelNotFoundException, ObjectNotFoundException,
                                    ResponseNotOkException)
from service_api.models import (City, CityXRefService, Service, State, StateXRefService)
from service_api.schemas import CityXRefServiceSchema, StateXRefServiceSchema
from service_api.utils import load_data, recognize_by_alias, send_request
from service_api.utils.loaders_interfaces import XRefBaseLoader
from .limitation import DomriaLimitationSystem

class DomriaCityXRefServicesLoader(XRefBaseLoader):
    """
    Fill table cityTypeXRefServices with domria original_ids
    """

    def load(self, *args, **kwargs) -> Dict[int, int]:
        """
        Loads data to city cross reference service table
        """
        state_ids: List[int] = args[0]
        with session_scope() as session:
            smt = select(State.id).order_by(State.id)
            state_ids = state_ids or [state_id for state_id, *_ in session.execute(smt).all()]
        status = {}

        for state_id in state_ids:
            try:
                status[state_id] = self.load_cities_by_state(state_id=state_id)
            except ObjectNotFoundException as error:
                LOGGER.error(error.desc)
            except KeyError as error:
                LOGGER.error(error)
            except ResponseNotOkException as error:
                LOGGER.error(error)

        return status

    def load_cities_by_state(self, **kwargs: int) -> int:
        """
        Getting cities from DOMRIA by original state_id
        Returns amount of fetched cities
        :param: state_id: int
        :return: int
        """
        state_id = kwargs.get("state_id")
        if state_id is None:
            raise KeyError("No parameter state_id provided in function load")

        with session_scope() as session:
            state = session.query(State).filter(State.id == state_id,
                                                State.version == VERSION_DEFAULT_TIMESTAMP).first()

        if state is None:
            raise ObjectNotFoundException(message="No such state_id in DB")

        domria_cities_meta = self.domria_meta["urls"]["cities"]

        with session_scope() as session:
            service = session.query(Service).filter_by(name=self.domria_meta["name"]).first()
            if service is None:
                raise ObjectNotFoundException(desc="No service {} found".format(self.domria_meta["name"]))
            state_xref = session.query(StateXRefService).get({"entity_id": state_id, "service_id": service.id})
            if state_xref is None:
                raise ObjectNotFoundException(desc="No StateXrefService obj found")

            set_by_state = session.query(City).filter_by(state_id=state_id)

        response = send_request("GET", "{}/{}/{}".format(self.domria_meta["base_url"], domria_cities_meta["url_prefix"],
                                                         state_xref.original_id),
                                params={
                                    "lang_id": self.domria_meta["optional"]["lang_id"],
                                    self.domria_meta["token_name"]: DomriaLimitationSystem.get_token()})
        if not response.ok:
            raise ResponseNotOkException(response.text)

        counter = 0
        for city_from_service in response.json():

            try:
                city = recognize_by_alias(City, city_from_service[domria_cities_meta["fields"]["name"]], set_by_state)
            except ModelNotFoundException as error:
                LOGGER.error(error)
                continue
            except ObjectNotFoundException as error:
                LOGGER.error(error)
                continue

            data = {
                "entity_id": city.id,
                "service_id": service.id,
                "original_id": str(city_from_service[domria_cities_meta["fields"]["original_id"]])
            }

            try:
                load_data(CityXRefServiceSchema(), data, CityXRefService)
            except ValidationError as error:
                LOGGER.error(error)
            except AlreadyInDbException as error:
                LOGGER.warning(error)
                continue
            else:
                counter += 1

        return counter


class DomriaStateXRefServicesLoader(XRefBaseLoader):
    """
    Class for filling db with domria state xref reference
    """

    def load(self, *args, **kwargs) -> int:
        """
        Getting states from DOMRIA
        Returns amount of fetched states
        :return: int
        """

        domria_states_meta = self.domria_meta["urls"]["states"]

        params = {
            "lang_id": self.domria_meta["optional"]["lang_id"],
            "api_key": DomriaLimitationSystem.get_token()
        }

        with session_scope() as session:
            service = session.query(Service).filter_by(name=self.domria_meta["name"]).first()
            if service is None:
                raise ObjectNotFoundException(desc="No service {} found".format(self.domria_meta["name"]))

        url = "{}/{}".format(self.domria_meta["base_url"], domria_states_meta["url_prefix"])
        response = send_request("GET", url, params=params)
        if not response.ok:
            raise RequestException(response.text)

        counter = 0
        for service_state in response.json():
            try:
                state = recognize_by_alias(State, service_state[domria_states_meta["fields"]["name"]])
            except ModelNotFoundException as error:
                LOGGER.error(error)
                continue
            except ObjectNotFoundException as error:
                LOGGER.error(error)
                continue

            data = {
                "entity_id": state.id,
                "service_id": service.id,
                "original_id": str(service_state[domria_states_meta["fields"]["original_id"]])
            }

            try:
                load_data(StateXRefServiceSchema(), data, StateXRefService)
            except ValidationError as error:
                LOGGER.error(error)
            except AlreadyInDbException as error:
                LOGGER.warning(error)
                continue
            else:
                counter += 1

        return counter
