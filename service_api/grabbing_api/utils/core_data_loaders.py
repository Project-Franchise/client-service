"""
Module with data Loaders
"""
import csv
from abc import ABC, abstractmethod
from typing import Dict, List

import requests
from marshmallow.exceptions import ValidationError
from requests.exceptions import RequestException
from sqlalchemy import select
from service_api import session_scope
from service_api.constants import VERSION_DEFAULT_TIMESTAMP
from service_api.exceptions import (ModelNotFoundException,
                                    ObjectNotFoundException,
                                    ResponseNotOkException)
from service_api.grabbing_api.constants import (
    DOMRIA_TOKEN, PATH_TO_CITIES_ALIASES_CSV, PATH_TO_CITIES_CSV, PATH_TO_METADATA, PATH_TO_OPERATION_TYPE_ALIASES_CSV,
    PATH_TO_OPERATION_TYPE_CSV, PATH_TO_REALTY_TYPE_ALIASES_CSV, PATH_TO_REALTY_TYPE_CSV, PATH_TO_SERVICES_CSV,
    PATH_TO_STATE_ALIASES_CSV, PATH_TO_STATE_CSV)
from service_api.models import (City, CityAlias, CityToService, OperationType, OperationTypeAlias,
                                OperationTypeToService, RealtyType, RealtyTypeAlias, RealtyTypeToService,
                                Service, State, StateAlias, StateToService)
from service_api.schemas import (CityAliasSchema, CitySchema, CityToServiceSchema, OperationTypeAliasSchema,
                                 OperationTypeSchema, OperationTypeToServiceSchema, RealtyTypeAliasSchema,
                                 RealtyTypeSchema, RealtyTypeToServiceSchema, ServiceSchema,
                                 StateAliasSchema, StateSchema, StateToServiceSchema)


from .grabbing_utils import load_data, open_metadata, recognize_by_alias


class BaseLoader(ABC):
    """
    Abstract class for loading static base date to DB (exmp. cities, states, realty_types...)
    """

    def __init__(self) -> None:
        """
        Fetches info from metadata
        """
        self.metadata = open_metadata(PATH_TO_METADATA)

    @abstractmethod
    def load(self, *args, **kwargs) -> None:
        """
        Main function of retrieving and loading data to db
        """
        return None


class XRefBaseLoader(BaseLoader):
    """
    Base Loader for cross reference tables
    """

    def __init__(self) -> None:
        """
        Loads domria metadata
        """
        super().__init__()
        self.domria_meta = self.metadata["DOMRIA API"]


class CSVLoader(BaseLoader):
    """
    Aliases loader from csv file
    Class attributes that must be initialized:
        model: Alias model
        model_schema: Alias schema
        path_to_file: str
    """

    @property
    @abstractmethod
    def model(self):
        """
        Alias model
        """
        ...

    @property
    @abstractmethod
    def model_schema(self):
        """
        Alias schema for model
        """
        ...

    @property
    @abstractmethod
    def path_to_file(self):
        """
        Path to aliases csv file
        """
        ...

    def __init__(self) -> None:
        """
        Open and load info from csv file
        """
        with open(self.path_to_file, encoding="utf-8", mode="r") as file:
            self.data = list(csv.DictReader(file))

    def load(self, *args, **kwargs) -> None:
        """
        Load models from csv file located in path_to_file
        """
        for row in self.data:
            load_data(row, self.model, self.model_schema)


class CityLoader(CSVLoader):
    """
    Loads cities to db
    """

    model = City
    model_schema = CitySchema
    path_to_file = PATH_TO_CITIES_CSV


class CityAliasesLoader(CSVLoader):
    """
    Loads city aliases to db
    """

    model = CityAlias
    model_schema = CityAliasSchema
    path_to_file = PATH_TO_CITIES_ALIASES_CSV


class StateLoader(CSVLoader):
    """
    Loads sates to db
    """

    model = State
    model_schema = StateSchema
    path_to_file = PATH_TO_STATE_CSV


class StateAliasesLoader(CSVLoader):
    """
    Loads sate aliases to db
    """

    model = StateAlias
    model_schema = StateAliasSchema
    path_to_file = PATH_TO_STATE_ALIASES_CSV


class ServiceLoader(CSVLoader):
    """
    Loads service to db
    """

    model = Service
    model_schema = ServiceSchema
    path_to_file = PATH_TO_SERVICES_CSV


class RealtyTypeLoader(CSVLoader):
    """
    Loads RealtyType from metadata
    """

    model = RealtyType
    model_schema = RealtyTypeSchema
    path_to_file = PATH_TO_REALTY_TYPE_CSV


class OperationTypeLoader(CSVLoader):
    """
    Loads OperationType from metadata
    """

    model = OperationType
    model_schema = OperationTypeSchema
    path_to_file = PATH_TO_OPERATION_TYPE_CSV


class OperationTypeAliasesLoader(CSVLoader):
    """
    Loads operation types aliases from csv file
    """

    model = OperationTypeAlias
    model_schema = OperationTypeAliasSchema
    path_to_file = PATH_TO_OPERATION_TYPE_ALIASES_CSV


class RealtyTypeAliasesLoader(CSVLoader):
    """
    Loads realty types aliases from csv file
    """

    model = RealtyTypeAlias
    model_schema = RealtyTypeAliasSchema
    path_to_file = PATH_TO_REALTY_TYPE_ALIASES_CSV


class OperationTypeXRefServicesLoader(XRefBaseLoader):
    """
    Fill table opertaionTypeXRefServices with original_ids
    """

    def load(self, *args, **kwargs) -> None:
        """
        Loads data to operation type cross reference service table
        """
        for service_name, service_meta in self.metadata.items():
            with session_scope() as session:
                service = session.query(Service).filter(Service.name == service_name).first()

                if service is None:
                    raise ObjectNotFoundException(desc=f"No service {service_name} found")

            for name, value in service_meta["url_characteristics"]["operation_type"].items():
                try:
                    obj = recognize_by_alias(OperationType, name)
                except ModelNotFoundException as error:
                    print(error)
                    continue
                except ObjectNotFoundException as error:
                    print(error)
                    continue

                data = {
                    "operation_type_id": obj.self_id,
                    "service_id": service.id,
                    "original_id": str(value)
                }

                load_data(data, OperationTypeToService, OperationTypeToServiceSchema)


class RealtyTypeXRefServicesLoader(XRefBaseLoader):
    """
    Fill table realtyTypeXRefServices with original_ids
    """

    def load(self, *args, **kwargs) -> None:
        """
        Loads data to realty type cross reference service table
        """
        for service_name, service_meta in self.metadata.items():
            with session_scope() as session:
                service = session.query(Service).filter(Service.name == service_name).first()

                if service is None:
                    raise ObjectNotFoundException(desc=f"No service {service_name} found")

            for name, value in service_meta["url_characteristics"]["realty_type"].items():
                try:
                    obj = recognize_by_alias(RealtyType, name)
                except ModelNotFoundException as error:
                    print(error)
                    continue
                except ObjectNotFoundException as error:
                    print(error)
                    continue

                data = {
                    "realty_type_id": obj.self_id,
                    "service_id": service.id,
                    "original_id": str(value)
                }

                load_data(data, RealtyTypeToService, RealtyTypeToServiceSchema)


class CityXRefServicesLoader(XRefBaseLoader):
    """
    Fill table cityTypeXRefServices with original_ids
    """

    def load(self, *args, **kwargs) -> Dict[int, int]:
        """
        Loads data to city cross reference service table
        """
        state_ids: List[int] = args[0]
        with session_scope() as session:
            smt = select(State.self_id).order_by(State.self_id)
            state_ids = state_ids or [state_id for state_id, *_ in session.execute(smt).all()]
        status = {}

        for state_id in state_ids:
            try:
                status[state_id] = self.load_cities_by_state(state_id=state_id)
            except ObjectNotFoundException as error:
                print(error)
            except KeyError as error:
                print(error)
            except ResponseNotOkException as error:
                print(error)

        return status

    def load_cities_by_state(self, **kwargs: int) -> int:
        """
        Getting cities from DOMRIA by original state_id
        Returns amount of fetched cities
        :param: state_id: int
        :return: int
        """

        if (state_id := kwargs.get("state_id")) is None:
            raise KeyError("No parameter state_id provided in function load")

        with session_scope() as session:
            state = session.query(State).filter(State.self_id == state_id,
                                                State.version == VERSION_DEFAULT_TIMESTAMP).first()

        if state is None:
            raise ObjectNotFoundException(message="No such state_id in DB")

        domria_cities_meta = self.domria_meta["url_rules"]["cities"]

        with session_scope() as session:
            service = session.query(Service).filter_by(name="DOMRIA API").first()
            if service is None:
                raise ObjectNotFoundException(desc="No service Domria found")
            state_xref = session.query(StateToService).get({"state_id": state_id, "service_id": service.id})
            if state_xref is None:
                raise ObjectNotFoundException(desc="No StateXrefServite obj  found")

            set_by_state = session.query(City).join(CityAlias, CityAlias.city_id ==
                                                    City.self_id).where(City.state_id == state_id)

        response = requests.get("{}{}/{}".format(self.domria_meta["base_url"],
                                                 domria_cities_meta["url_prefix"],
                                                 state_xref.original_id),
                                params={
            "lang_id": self.domria_meta["optional"]["lang_id"],
            "api_key": DOMRIA_TOKEN
        }
        )
        if not response.ok:
            raise ResponseNotOkException(response.text)

        counter = 0
        for city_from_service in response.json():
            try:
                city = recognize_by_alias(City, city_from_service[domria_cities_meta["filters"]["name"]], set_by_state)
            except ModelNotFoundException as error:
                print(error)
                continue
            except ObjectNotFoundException as error:
                print(error)
                continue

            data = {
                "city_id": city.self_id,
                "service_id": service.id,
                "original_id": str(city_from_service[domria_cities_meta["filters"]["original_id"]])
            }

            try:
                load_data(data, CityToService, CityToServiceSchema)
            except ValidationError as error:
                print(error)
            else:
                counter += 1

        return counter


class StateXRefServicesLoader(XRefBaseLoader):
    """
    Class for filling db with state xref reference
    """

    def load(self, *args, **kwargs) -> int:
        """
        Getting states from DOMRIA
        Returns amount of fetched states
        :return: int
        """

        domria_states_meta = self.domria_meta["url_rules"]["states"]

        params = {
            "lang_id": self.domria_meta["optional"]["lang_id"],
            "api_key": DOMRIA_TOKEN
        }

        with session_scope() as session:
            service = session.query(Service).filter_by(name="DOMRIA API").first()
            if service is None:
                raise ObjectNotFoundException(desc="No service Domria found")

        url = "{}{}".format(self.domria_meta["base_url"], domria_states_meta["url_prefix"])
        response = requests.get(url, params=params)
        if not response.ok:
            raise RequestException(response.text)

        counter = 0
        for service_state in response.json():
            try:
                state = recognize_by_alias(State, service_state[domria_states_meta["filters"]["name"]])
            except ModelNotFoundException as error:
                print(error)
                continue
            except ObjectNotFoundException as error:
                print(error)
                continue

            data = {
                "state_id": state.self_id,
                "service_id": service.id,
                "original_id": str(service_state[domria_states_meta["filters"]["original_id"]])
            }

            try:
                load_data(data, StateToService, StateToServiceSchema)
            except ValidationError as error:
                print(error)
            else:
                counter += 1

        return counter
