"""
Fixtures for testing converters
"""
import json
import os
from typing import Dict, List

import pytest

from service_api import LOGGER, session_scope, Base, engine
from service_api.constants import PATH_TO_METADATA
from service_api.exceptions import LoadDataError
from service_api.utils import open_metadata
from tests.convertors import ServiceModelConvertor, OperationTypeModelConvertor, RealtyDetailsModelConvertor, \
    CategoryModelConvertor, StateModelConvertor, RealtyModelConvertor, RealtyTypeModelConvertor, CityModelConvertor, \
    AbstractModelConvertor, StateAliasModelConvertor, CityAliasModelConvertor, OperationTypeAliasModelConvertor, \
    RealtyTypeAliasModelConvertor, CityXRefServiceModelConvertor, StateXRefServiceModelConvertor, \
    OperationTypeXRefServiceModelConvertor, RealtyTypeXRefServiceModelConvertor

path_to_domria_test_data = ["tests", "static_data", "services_test_data", "domria_test_data"]
PATH_TO_TEST_DATA = os.sep.join([*path_to_domria_test_data, "test_db_data.json"])


@pytest.fixture(scope="class")
def get_metadata():
    """
    Return metadata to test converters
    """
    return open_metadata(PATH_TO_METADATA)["DOMRIA API"]


@pytest.fixture(scope="module")
def open_testing_data():
    """
    Open file with testing data and return content
    :param path: path to test data
    :return: dict with test data
    """
    def open_specific_file(path: str) -> Dict:
        try:
            with open(path, encoding="utf-8") as data_file:
                testing_data = json.load(data_file)
        except json.JSONDecodeError as error:
            LOGGER.error(error)
            raise LoadDataError from error
        except FileNotFoundError as error:
            LOGGER.error("Invalid testing data path, or test_data.json file does not exist")
            raise LoadDataError from error
        return testing_data
    return open_specific_file


@pytest.fixture(scope="class")
def get_model_convertors() -> List[AbstractModelConvertor]:
    """
    Function to get all Model convertors
    :return: List[AbstractModelConvertor]
    """
    return [ServiceModelConvertor(), CategoryModelConvertor(), RealtyTypeModelConvertor(),
            OperationTypeModelConvertor(), StateModelConvertor(), CityModelConvertor(),
            RealtyDetailsModelConvertor(), RealtyModelConvertor(), StateAliasModelConvertor(),
            RealtyTypeAliasModelConvertor(), OperationTypeAliasModelConvertor(), CityAliasModelConvertor(),
            OperationTypeXRefServiceModelConvertor(), RealtyTypeXRefServiceModelConvertor(),
            StateXRefServiceModelConvertor(), CityXRefServiceModelConvertor()]


@pytest.fixture(scope="class")
def fill_db_with_test_data(get_model_convertors, open_testing_data):
    """
    Function for filling testing database
    """
    def fill_db():
        ready_objects = []
        model_convertors = get_model_convertors

        testing_data = open_testing_data(PATH_TO_TEST_DATA)
        for convertor, obj_container in zip(model_convertors, testing_data):
            ready_objects.extend(convertor.convert_to_model(testing_data[obj_container]))

        with session_scope() as session:
            session.add_all(ready_objects)
            session.commit()
            ready_objects.clear()
    return fill_db


@pytest.fixture(scope="class")
def database(fill_db_with_test_data):
    """
    Create all tables in test db and fill with test data
    """
    Base.metadata.create_all(engine)
    fill_db_with_test_data()
    yield
    with session_scope() as session:
        session.close()
        Base.metadata.drop_all(engine)
