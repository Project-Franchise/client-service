"""
Convertors testing module
"""
import json
from typing import Dict, List

import pytest

from service_api import Base, engine
from service_api import LOGGER, session_scope
from service_api.constants import PATH_TO_METADATA
from service_api.exceptions import LoadDataError
from service_api.services.domria.convertors import DomRiaOutputConverter
from service_api.utils import open_metadata
from tests.convertors import ServiceModelConvertor, OperationTypeModelConvertor, RealtyDetailsModelConvertor, \
    CategoryModelConvertor, StateModelConvertor, RealtyModelConvertor, RealtyTypeModelConvertor, CityModelConvertor, \
    AbstractModelConvertor, StateAliasModelConvertor, CityAliasModelConvertor, OperationTypeAliasModelConvertor, \
    RealtyTypeAliasModelConvertor

PATH_TO_TEST_DATA = r"tests\static_data\services_test_data\domria_test_data\test_db_data.json"


# @pytest.fixture()
def open_testing_data(path: str) -> Dict:
    """
    Open file with testing data and return content
    :param path: path to test data
    :return: dict with test data
    """
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


# @pytest.fixture()
def fill_db_with_test_data():
    """
    Function for filling testing database
    """
    ready_objects = []
    model_convertors = get_model_convertors()

    testing_data = open_testing_data(PATH_TO_TEST_DATA)
    for convertor, obj_container in zip(model_convertors, testing_data):
        ready_objects.extend(convertor.convert_to_model(testing_data[obj_container]))

    with session_scope() as session:
        session.add_all(ready_objects)
        session.commit()
        ready_objects.clear()


# @pytest.fixture()
def get_model_convertors() -> List[AbstractModelConvertor]:
    """
    Function to get all Model convertors
    :return: List[AbstractModelConvertor]
    """
    return [ServiceModelConvertor(), CategoryModelConvertor(), RealtyTypeModelConvertor(),
            OperationTypeModelConvertor(), StateModelConvertor(), CityModelConvertor(),
            RealtyDetailsModelConvertor(), RealtyModelConvertor(), StateAliasModelConvertor(),
            RealtyTypeAliasModelConvertor(), OperationTypeAliasModelConvertor(), CityAliasModelConvertor()]


def setup_function():
    """
    Create all table and instances in DB
    """
    Base.metadata.create_all(engine)


def teardown_function():
    """
    Closes sql_session if its open and drop database
    """
    with session_scope() as session:
        session.close()
        Base.metadata.drop_all(engine)


def get_convertors_data():
    """
    Return input and expected data to test converters
    """
    with open('tests/static_data/services_test_data/domria_test_data/convertors_test_data.json', "r") as file:
        data = json.loads(file.read())
    return data


@pytest.fixture()
def get_metadata():
    """
    Return metadata to test converters
    """
    return open_metadata(PATH_TO_METADATA)["DOMRIA API"]


# class TestDomRiaOutputConverter:
@pytest.mark.parametrize(("expected_realty_data", "expected_realty_details", "response"),
                         [list(unit.values()) for unit in get_convertors_data()])
def test_make_realty_details_data(expected_realty_data, expected_realty_details, response):
    """
    Check make_realty_data and make_realty_details methods in DomRiaOutputConverter
    """
    fill_db_with_test_data()
    converter = DomRiaOutputConverter(response, open_metadata(PATH_TO_METADATA)["DOMRIA API"])
    converter.make_realty_details_data()
    converter.make_realty_data()


# @pytest.fixture(scope="function")
# def rnd_gen():
#     return random.Random(123456)
#
#
# @pytest.fixture(scope="function")
# def rnd(rnd_gen):
#     return rnd_gen.random()
#
#
# @pytest.fixture()
# def fixture_1(rnd):
#     return rnd
#
#
# @pytest.fixture()
# def fixture_2(rnd):
#     return rnd
#
#
# def test_training(fixture_1, fixture_2):
#     assert fixture_1 == fixture_2
#
#
# def test_training2():
#     assert 2 == 2
