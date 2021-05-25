"""
Olx loaders
"""
from typing import Dict

from bs4 import BeautifulSoup
from marshmallow.exceptions import ValidationError

from service_api import LOGGER, session_scope
from service_api.constants import VERSION_DEFAULT_TIMESTAMP
from service_api.exceptions import (AlreadyInDbException, ModelNotFoundException, ObjectNotFoundException)
from service_api.models import (City, CityXRefService, Service, State, StateXRefService)
from service_api.schemas import CityXRefServiceSchema, StateXRefServiceSchema
from service_api.utils import load_data, recognize_by_alias
from service_api.utils.selenium import init_driver
from service_api.utils.loaders_interfaces import BaseLoader


class OlxXRefBaseLoader(BaseLoader):
    """
    Base Loader for cross reference tables for olx
    """

    def __init__(self) -> None:
        """
        Loads olx metadata
        """
        super().__init__()
        self.olx_meta = self.metadata["OLX"]


class OlxStateXRefServicesLoader(OlxXRefBaseLoader):
    """
    Class for filling db with state xref reference from olx
    """

    @staticmethod
    def get_states() -> dict:
        """
        Navigating through site olx.com and getting states
        :return: dict
        """
        driver = init_driver("https://www.olx.ua/uk/nedvizhimost/kvartiry-komnaty/arenda-kvartir-komnat/")
        driver.execute_script("arguments[0].click();", driver.find_element_by_id("cityField"))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all("a", class_="link gray")
        urls = {}

        with session_scope() as session:
            states = session.query(State).all()

        states = [state.name for state in states]

        for item in items:
            text = item.get_text()
            if text.split(" ")[0] in states:
                urls[text.split()[0]] = ((item.get("href")).split("/"))[-2]
        return urls

    def load(self, *args, **kwargs) -> int:
        """
        Load states from OLX
        Returns amount of fetched states
        :return: int
        """

        with session_scope() as session:
            service = session.query(Service).filter_by(name=self.olx_meta["name"]).first()
            if service is None:
                raise ObjectNotFoundException(desc="No service {} found".format(self.olx_meta["name"]))

        service_states = OlxStateXRefServicesLoader.get_states()
        counter = 0
        for state, url in service_states.items():
            try:
                state_from_alias = recognize_by_alias(State, state)
            except ModelNotFoundException as error:
                LOGGER.error(error)
                continue
            except ObjectNotFoundException as error:
                LOGGER.error(error)
                continue

            data = {
                "entity_id": state_from_alias.id,
                "service_id": service.id,
                "original_id": url
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


class OlxCityXRefServicesLoader(OlxXRefBaseLoader):
    """
    Fill table cityTypeXRefServices with original_ids from olx
    """

    def get_cities_by_state(self, html, state, urls):
        """
        Getting all cities by particular state from olx
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("a", class_="regionSelectA2")

        if not items:
            return {}

        with session_scope() as session:
            state = session.query(State).filter_by(name=state).first()
            cities_object = session.query(
                City).filter_by(state_id=state.id).all()

        cities = [city.name for city in cities_object]
        urls[state.name] = {}

        for item in items:
            if item.get_text() in cities:
                urls[state.name][item.get_text()] = item.get("data-url")
        return urls

    def get_all_cities(self):
        """
        getting all cities from olx
        :return: dict
        """
        driver = init_driver("https://www.olx.ua/uk/nedvizhimost/kvartiry-komnaty/arenda-kvartir-komnat/")
        driver.execute_script("arguments[0].click();", driver.find_element_by_id("cityField"))
        olx_states = self.olx_meta["entities"]["states"]
        urls_cities = {}
        for key, value in olx_states.items():
            cities = {}
            while not cities:
                driver.execute_script("arguments[0].click();",
                                      driver.find_element_by_css_selector(f'a[data-id="{value}"]'))
                cities = self.get_cities_by_state(driver.page_source, key, cities)
            driver.execute_script("arguments[0].click();",
                                  driver.find_element_by_css_selector("a[id=back_region_link]"))
            for state, dict_of_cities in cities.items():
                urls_cities[state] = dict_of_cities
        return urls_cities

    def load(self, *args, **kwargs) -> Dict[int, int]:
        """
        Loads data to city cross reference service table
        """
        status = {}

        response_from_olx = self.get_all_cities()

        for state_name, cities in response_from_olx.items():
            try:
                status[state_name] = self.load_cities_by_state(state_name=state_name, cities=cities)
            except ObjectNotFoundException as error:
                LOGGER.error(error.desc)
            except KeyError as error:
                LOGGER.error(error)

        return status

    def load_cities_by_state(self, **kwargs) -> int:
        """
        loading cities from OLX to database by each state separately
        Returns amount of fetched cities
        :param: state_id: int
        :return: int
        """

        if (state_name := kwargs.get("state_name")) is None:
            raise KeyError("No parameter state_id provided in function load")

        with session_scope() as session:
            state = session.query(State).filter(State.name == state_name,
                                                State.version == VERSION_DEFAULT_TIMESTAMP).first()

        if state is None:
            raise ObjectNotFoundException(message="No such state_id in DB")

        with session_scope() as session:
            service = session.query(Service).filter_by(name=self.olx_meta["name"]).first()
            if service is None:
                raise ObjectNotFoundException(desc="No service {} found".format(self.olx_meta["name"]))

            set_by_state = session.query(City).filter_by(state_id=state.id)

        counter = 0
        cities = kwargs.get("cities")

        for city, original_id in cities.items():
            try:
                city = recognize_by_alias(City, city, set_by_state)
            except ModelNotFoundException as error:
                LOGGER.error(error)
                continue
            except ObjectNotFoundException as error:
                LOGGER.error(error)
                continue

            data = {
                "entity_id": city.id,
                "service_id": service.id,
                "original_id": original_id
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
