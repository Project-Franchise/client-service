"""
Module with data Loaders
"""
from typing import Dict, List

from service_api import LOGGER, session_scope
from service_api.services import city_loaders, state_loaders
from service_api.exceptions import (AlreadyInDbException, ModelNotFoundException, ObjectNotFoundException)
from service_api.models import (Category, CategoryAlias, CategoryXRefService, City, CityAlias,  OperationType,
                                OperationTypeAlias, OperationTypeXRefService, Realty, RealtyDetails, RealtyType,
                                RealtyTypeAlias, RealtyTypeXRefService, Service, State, StateAlias)
from service_api.schemas import (CategoryAliasSchema, CategorySchema, CategoryXRefServiceSchema, CityAliasSchema,
                                 CitySchema, OperationTypeAliasSchema, OperationTypeSchema,
                                 OperationTypeXRefServiceSchema, RealtyDetailsSchema, RealtySchema,
                                 RealtyTypeAliasSchema, RealtyTypeSchema, RealtyTypeXRefServiceSchema, ServiceSchema,
                                 StateAliasSchema, StateSchema)
from ..constants import (PATH_TO_CATEGORIES_CSV, PATH_TO_CATEGORY_ALIASES_CSV, PATH_TO_CITIES_ALIASES_CSV,
                         PATH_TO_CITIES_CSV, PATH_TO_OPERATION_TYPE_ALIASES_CSV,
                         PATH_TO_OPERATION_TYPE_CSV, PATH_TO_REALTY_TYPE_ALIASES_CSV,
                         PATH_TO_REALTY_TYPE_CSV, PATH_TO_SERVICES_CSV, PATH_TO_STATE_ALIASES_CSV, PATH_TO_STATE_CSV)
from ..utils import load_data, recognize_by_alias
from .loaders_interfaces import XRefBaseLoader, CSVLoader


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
        for service_name, service_meta in self.metadata.items():
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
                    load_data(OperationTypeXRefServiceSchema(), data, OperationTypeXRefService)
                except AlreadyInDbException as error:
                    LOGGER.warning(error)
                    continue


class RealtyTypeXRefServicesLoader(XRefBaseLoader):
    """
    Fill table realtyTypeXRefServices with domria original_ids
    """

    def load(self, *args, **kwargs) -> None:
        """
        Loads data to realty type cross reference service table
        """
        for service_name, service_meta in self.metadata.items():
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
                    load_data(RealtyTypeXRefServiceSchema(), data, RealtyTypeXRefService)
                except AlreadyInDbException as error:
                    LOGGER.warning(error)
                    continue


class CategoryXRefServicesLoader(XRefBaseLoader):
    """
    Fill table CategoryXRefServices with domria original_ids
    """

    def load(self, *args, **kwargs) -> None:
        """
        Loads data to category cross reference service table
        """
        for service_name, service_meta in self.metadata.items():
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
                    load_data(CategoryXRefServiceSchema(), data, CategoryXRefService)
                except AlreadyInDbException as error:
                    LOGGER.warning(error)
                    continue


class CityXRefServicesLoader(XRefBaseLoader):
    """
    Main class for loading cities xref tables for each service
    """
    LOADERS = city_loaders

    def load(self, *args, **kwargs) -> None:
        for service, loader in self.LOADERS.items():
            LOGGER.debug("Loading city xref for %s", service)
            loader().load(*args, **kwargs)


class StateXRefServicesLoader(XRefBaseLoader):
    """
    Main class for loading states xref tables for each service
    """
    LOADERS = state_loaders

    def load(self, *args, **kwargs) -> None:
        for service, loader in self.LOADERS.items():
            LOGGER.debug("Loading state xref for %s", service)
            loader().load(*args, **kwargs)


class RealtyLoader:
    """
    Load realty data to db
    """

    def load(self, all_data: List[Dict]) -> List[Dict]:
        """
         Calls mapped loader classes for keys in params dict input
        :params: List[Dict] - list of realty
        :return: None - the only loader's responsibility is to load realty and realty details to the database
        """
        result = []
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
                result.append(RealtySchema().dump(load_data(RealtySchema(), realty, Realty)))
            except KeyError as error:
                print(error.args)
            except AlreadyInDbException as error:
                print(error)
                continue

        return result
