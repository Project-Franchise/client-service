"""
Module with data Loaders
"""
import csv
from abc import ABC, abstractmethod

from typing import Dict, List

from marshmallow.exceptions import ValidationError
from requests.exceptions import RequestException
from sqlalchemy import select

from service_api import session_scope, LOGGER
from service_api.utils import send_request
from service_api.constants import VERSION_DEFAULT_TIMESTAMP
from service_api.exceptions import (ModelNotFoundException, ObjectNotFoundException,
                                    ResponseNotOkException, AlreadyInDbException)
from service_api.grabbing_api.constants import (
    PATH_TO_CITIES_ALIASES_CSV, PATH_TO_CITIES_CSV, PATH_TO_METADATA, PATH_TO_OPERATION_TYPE_ALIASES_CSV,
    PATH_TO_OPERATION_TYPE_CSV, PATH_TO_REALTY_TYPE_ALIASES_CSV, PATH_TO_REALTY_TYPE_CSV, PATH_TO_SERVICES_CSV,
    PATH_TO_STATE_ALIASES_CSV, PATH_TO_STATE_CSV, PATH_TO_CATEGORIES_CSV, PATH_TO_CATEGORY_ALIASES_CSV)
from service_api.models import (City, CityAlias, CityToService, OperationType, OperationTypeAlias,
                                OperationTypeToService, RealtyType, RealtyTypeAlias, RealtyTypeToService,
                                Service, State, StateAlias, StateToService, Category, CategoryAlias, CategoryToService,
                                Realty, RealtyDetails)
from service_api.schemas import (CityAliasSchema, CitySchema, CityToServiceSchema, OperationTypeAliasSchema,
                                 OperationTypeSchema, OperationTypeToServiceSchema, RealtyTypeAliasSchema,
                                 RealtyTypeSchema, RealtyTypeToServiceSchema, ServiceSchema, StateAliasSchema,
                                 StateSchema, StateToServiceSchema, CategorySchema, CategoryAliasSchema,
                                 CategoryToServiceSchema, RealtySchema, RealtyDetailsSchema)
from service_api.grabbing_api.utils.limitation import DomriaLimitationSystem
from .grabbing_utils import (load_data, open_metadata, recognize_by_alias)


class BaseLoader(ABC):
    """
    Abstract class for loading static base date to DB (exp. cities, states, realty_types...)
    """

    def __init__(self) -> None:
        """
        Fetches info from metadata
        Raise MetaDataError
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
            try:
                load_data(self.model_schema(), row, self.model)
            except AlreadyInDbException as error:
                LOGGER.warning(error)
                continue


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


class CategoryLoader(CSVLoader):
    """
    Loads Categories from metadata
    """

    model = Category
    model_schema = CategorySchema
    path_to_file = PATH_TO_CATEGORIES_CSV


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


class CategoryAliasesLoader(CSVLoader):
    """
    Loads realty types aliases from csv file
    """

    model = CategoryAlias
    model_schema = CategoryAliasSchema
    path_to_file = PATH_TO_CATEGORY_ALIASES_CSV


class OperationTypeXRefServicesLoader(XRefBaseLoader):
    """
    Fill table OperationTypeXRefServices with original_ids
    """

    def load(self, *args, **kwargs) -> None:
        """
        Loads data to operation type cross reference service table
        """
        service_name = "DOMRIA API"
        service_meta = self.metadata[service_name]
        with session_scope() as session:
            service = session.query(Service).filter(Service.name == service_name).first()

            if service is None:
                raise ObjectNotFoundException(desc="No service {} found".format(service_name))

        for name, value in service_meta["entities"]["operation_type"].items():
            try:
                obj = recognize_by_alias(OperationType, name)
            except ModelNotFoundException as error:
                LOGGER.error(error)
                continue
            except ObjectNotFoundException as error:
                LOGGER.error(error)
                continue

            data = {
                "entity_id": obj.id,
                "service_id": service.id,
                "original_id": str(value)
            }
            try:
                load_data(OperationTypeToServiceSchema(), data, OperationTypeToService)
            except AlreadyInDbException as error:
                LOGGER.warning(error)
                continue


class RealtyTypeXRefServicesLoader(XRefBaseLoader):
    """
    Fill table realtyTypeXRefServices with original_ids
    """

    def load(self, *args, **kwargs) -> None:
        """
        Loads data to realty type cross reference service table
        """
        service_name = "DOMRIA API"
        service_meta = self.metadata[service_name]
        with session_scope() as session:
            service = session.query(Service).filter(Service.name == service_name).first()

            if service is None:
                raise ObjectNotFoundException(desc="No service {} found".format(service_name))

        for name, value in service_meta["entities"]["realty_type"].items():
            try:
                obj = recognize_by_alias(RealtyType, name)
            except ModelNotFoundException as error:
                LOGGER.error(error)
                continue
            except ObjectNotFoundException as error:
                LOGGER.error(error)
                continue

            data = {
                "entity_id": obj.id,
                "service_id": service.id,
                "original_id": str(value)
            }
            try:
                load_data(RealtyTypeToServiceSchema(), data, RealtyTypeToService)
            except AlreadyInDbException as error:
                LOGGER.warning(error)
                continue


class CategoryXRefServicesLoader(XRefBaseLoader):
    """
    Fill table CategoryXRefServices with original_ids
    """

    def load(self, *args, **kwargs) -> None:
        """
        Loads data to category cross reference service table
        """
        service_name = "DOMRIA API"
        service_meta = self.metadata[service_name]
        with session_scope() as session:
            service = session.query(Service).filter(
                Service.name == service_name).first()

            if service is None:
                raise ObjectNotFoundException(
                    desc="No service {} found".format(service_name))

        for name, value in service_meta["entities"]["category"].items():
            try:
                obj = recognize_by_alias(Category, name)
            except ModelNotFoundException as error:
                LOGGER.error(error)
                continue
            except ObjectNotFoundException as error:
                LOGGER.error(error)
                continue

            data = {
                "entity_id": obj.id,
                "service_id": service.id,
                "original_id": str(value["own_id"])
            }
            try:
                load_data(CategoryToServiceSchema(), data, CategoryToService)
            except AlreadyInDbException as error:
                LOGGER.warning(error)
                continue


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
            state_xref = session.query(StateToService).get({"entity_id": state_id, "service_id": service.id})
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
                load_data(CityToServiceSchema(), data, CityToService)
            except ValidationError as error:
                LOGGER.error(error)
            except AlreadyInDbException as error:
                LOGGER.warning(error)
                continue
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
                load_data(StateToServiceSchema(), data, StateToService)
            except ValidationError as error:
                LOGGER.error(error)
            except AlreadyInDbException as error:
                LOGGER.warning(error)
                continue
            else:
                counter += 1

        return counter


class RealtyLoader:
    """
    Load realty data to db
    """

    def load(self, all_data: List[Dict]) -> None:
        """
         Calls mapped loader classes for keys in params dict input
        :params: List[Dict] - list of realty
        :return: None - the only loader's responsibility is to load realty and realty details to the database
        """
        for realty, realty_details_id in all_data:
            try:
                load_data(RealtyDetailsSchema(), realty_details_id, RealtyDetails)
            except KeyError as error:
                print(error.args)
            except AlreadyInDbException as error:
                print(error)
                continue

            with session_scope() as session:
                realty_details_id = session.query(RealtyDetails). \
                    filter_by(**realty_details_id).first().id
                realty["realty_details_id"] = realty_details_id
            try:
                load_data(RealtySchema(), realty, Realty)

            except KeyError as error:
                print(error.args)
            except AlreadyInDbException as error:
                print(error)
                continue
