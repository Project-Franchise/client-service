"""
Client Api testing module
"""
import os
from typing import Dict, List
from unittest.mock import patch

import pytest

from convertors import get_model_convertors, get_realty_template
from service_api import Base, engine, flask_app, session_scope
from service_api.client_api.resources import StateResource, StatesResource, \
    CityResource, CitiesResource, RealtyTypeResource, RealtyTypesResource, \
    OperationTypeResource, OperationTypesResource, RealtyResource
from service_api.errors import BadRequestException

path_to_tests_static_data = ["tests", "static_data"]
PATH_TO_TEST_DATA = os.sep.join([*path_to_tests_static_data, "test_data.json"])


@pytest.fixture(scope="module")
def fill_db_with_test_data(open_testing_data):
    """
    Function for filling testing database
    """
    def fill_db():
        ready_objects = []
        model_convertors = get_model_convertors()

        testing_data = open_testing_data(PATH_TO_TEST_DATA)
        for convertor, obj_container in zip(model_convertors, testing_data):
            ready_objects.extend(convertor.convert_to_model(testing_data[obj_container]))

        with session_scope() as session:
            session.add_all(ready_objects)
            session.commit()
            ready_objects.clear()
    return fill_db


def filter_test_data(filters: Dict, open_testing_data) -> List[Dict]:
    """
    Filter test data due to given filters
    :param filters: dict with data for filtration
    :return: filtered realties due to realty template
    """
    testing_data = open_testing_data(PATH_TO_TEST_DATA)
    filtered_data = []
    for realty, realty_details in zip(testing_data["realty_data"], testing_data["realty_details_data"]):
        if realty["realty_type_id"] == filters["realty_type_id"] and \
                realty["operation_type_id"] == filters["operation_type_id"] and \
                filters["price"]["ge"] <= realty_details["price"] <= filters["price"]["le"]:
            filtered_data.append(get_realty_template(realty, realty_details))
    return filtered_data


@pytest.fixture(scope="module")
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


@pytest.mark.parametrize("state_id", [1, 2, 3, 4, 5])
def test_get_state_by_id(state_id, database):
    """
    Checking the db response of state model by id
    """
    actual, response_code = StateResource().get(state_id=state_id)
    expected = {
        "id": state_id,
        "name": f"TestStateName{state_id}",
        "self_id": 110 + state_id
    }
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


def test_get_states(database):
    """
    Checking the db response of all state models
    """
    actual, response_code = StatesResource().get()
    expected = [{"self_id": 111, "name": "TestStateName1", "id": 1},
                {"self_id": 112, "name": "TestStateName2", "id": 2},
                {"self_id": 113, "name": "TestStateName3", "id": 3},
                {"self_id": 114, "name": "TestStateName4", "id": 4},
                {"self_id": 115, "name": "TestStateName5", "id": 5},
                ]
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


def test_get_realty_types(database):
    """
    Checking the db response of all realty_types
    """
    actual, response_code = RealtyTypesResource().get()
    expected = [{"self_id": 101, "name": "TestRealtyTypeName1", "id": 1},
                {"self_id": 102, "name": "TestRealtyTypeName2", "id": 2},
                {"self_id": 103, "name": "TestRealtyTypeName3", "id": 3},
                {"self_id": 104, "name": "TestRealtyTypeName4", "id": 4},
                ]
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


@pytest.mark.parametrize("realty_type_id", [1, 2, 3, 4])
def test_get_realty_type_by_id(realty_type_id, database):
    """
    Checking the db response of realty_type model by id
    """
    actual, response_code = RealtyTypeResource().get(realty_type_id=realty_type_id)
    expected = {
        "id": realty_type_id,
        "name": f"TestRealtyTypeName{realty_type_id}",
        "self_id": 100 + realty_type_id,
    }
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


def test_get_operation_types(database):
    """
    Checking the db response of all operation_types
    """
    actual, response_code = OperationTypesResource().get()
    expected = [{"self_id": 201, "name": "TestOperationTypeName1", "id": 1},
                {"self_id": 202, "name": "TestOperationTypeName2", "id": 2},
                {"self_id": 203, "name": "TestOperationTypeName3", "id": 3},
                ]
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


@pytest.mark.parametrize("operation_type_id", [1, 2, 3])
def test_get_operation_type_by_id(operation_type_id, database):
    """
    Checking the db response of operation type model by id
    """
    actual, response_code = OperationTypeResource().get(operation_type_id=operation_type_id)
    expected = {
        "id": operation_type_id,
        "name": f"TestOperationTypeName{operation_type_id}",
        "self_id": 200 + operation_type_id
    }
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


@pytest.mark.parametrize(
    "arguments,expected_exception",
    [({}, BadRequestException),
     ({
        "name": "Львів",
        "state_id": "sdf"
      }, BadRequestException),
     ({
        "name": "Львів",
        "state_id": "sdf"
      }, BadRequestException),
     ({
        "state_id": "sdf"
      }, BadRequestException),
     ({
        "state_id": "1000"
      }, BadRequestException),
     ])
def test_get_city_validate_exception(arguments, expected_exception, database):
    """
    Test route for getting city with validation method for exception
    """
    with flask_app.test_request_context():
        with patch("service_api.client_api.resources.request") as mock_request:
            mock_request.args.return_value = arguments
            mock_request.args.called_once()
        with pytest.raises(expected_exception):
            CityResource().get()


@pytest.mark.parametrize(
    "filters",
    [{
        "self_id": 310
     },
     {
        "id": 3,
        "self_id": 303
     },
     {
        "self_id": 305,
        "name": "TestCityName5"
     },
     {
        "state_id": 3,
        "self_id": 308
     },
     {
        "id": 7,
        "self_id": 307,
        "state_id": 3
     },
     {
        "id": 4,
        "self_id": 304,
        "name": "TestCityName4",
        "state_id": 2
     },
     {
        "self_id": 302,
        "name": "TestCityName2",
        "state_id": 1
     },
     {
        "id": 10,
        "name": "TestCityName10",
        "self_id": 310
     }])
def test_get_city_by_id(filters, database):
    """
    Test route for getting city by id
    """
    with flask_app.test_request_context():
        with patch("service_api.client_api.resources.request") as mock_request:
            mock_request.args = filters
            actual, response_code = CityResource().get()
            expected = [{
                "id": filters["self_id"] - 300,
                "name": "TestCityName{}".format(filters["self_id"] - 300),
                "self_id": filters["self_id"]
            }]
        expected_code = 200
        assert actual == expected
        assert response_code == expected_code


def test_get_cities(database):
    """
    Checking the db response of all cities
    """
    actual, response_code = CitiesResource().get()
    expected = [{"self_id": 301, "name": "TestCityName1", "id": 1},
                {"self_id": 302, "name": "TestCityName2", "id": 2},
                {"self_id": 303, "name": "TestCityName3", "id": 3},
                {"self_id": 304, "name": "TestCityName4", "id": 4},
                {"self_id": 305, "name": "TestCityName5", "id": 5},
                {"self_id": 306, "name": "TestCityName6", "id": 6},
                {"self_id": 307, "name": "TestCityName7", "id": 7},
                {"self_id": 308, "name": "TestCityName8", "id": 8},
                {"self_id": 309, "name": "TestCityName9", "id": 9},
                {"self_id": 310, "name": "TestCityName10", "id": 10},
                ]
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


@pytest.mark.parametrize(
    "filters,expected_exception",
    [({}, BadRequestException),
     ({
         "latest": 4
      }, BadRequestException),
     ({
         "price": {
             "le": 1290000,
             "ge": 10000
         },
         "page_ads_number": 10,
         "page": 1,
         "latest": [],
         "state_id": 2,
         "realty_type_id": 1,
         "operation_type_id": 1
      }, BadRequestException),
     ({
         "price": {
             "le": 1290000
         },
         "page_ads_number": 10,
         "page": 1,
         "latest": "latest",
         "state_id": 2
      }, BadRequestException),
     ({
          "price": {
              "le": 10000
          },
          "latest": True,
          "state_id": 1,
          "realty_type_id": 1,
          "operation_type_id": 1
      }, BadRequestException),
     ({
          "price": {
              "le": 10000
          },
          "page_ads_number": 1,
          "latest": True,
          "non_exist_param": 456,
          "state_id": 1,
          "realty_type_id": 1,
          "operation_type_id": 1
      }, BadRequestException),
     ({
          "page_ads_number": 1,
          "latest": True,
          "state_id": 1,
          "realty_type_id": 1,
          "operation_type_id": 1
      }, BadRequestException),
     ({
          "price": {
              "le": 10000,
              "ge": 10001
          },
          "page_ads_number": 1,
          "latest": True,
          "state_id": 1,
          "realty_type_id": 1,
          "operation_type_id": 1
      }, BadRequestException),
     ])
def test_filter_validation_for_getting_realty(filters, expected_exception, database):
    """
    Test route for getting realties from database with validation method for exception
    """
    with flask_app.test_request_context():
        with patch("service_api.client_api.resources.request.get_json") as mock_request:
            mock_request().return_value = filters
            mock_request().called_once()
            with pytest.raises(expected_exception):
                RealtyResource().post()


@pytest.mark.parametrize(
    "filters",
    [{
        "price": {
            "ge": 1000,
            "le": 88000
        },
        "realty_type_id": 1,
        "latest": False,
        "page": 1,
        "page_ads_number": 1,
        "operation_type_id": 1
     },
     {
        "price": {
            "ge": 1000,
            "le": 88000
        },
        "realty_type_id": 1,
        "latest": False,
        "page": 1,
        "page_ads_number": 2,
        "operation_type_id": 2
     },
     {
        "price": {
            "ge": 2000,
            "le": 14000
        },
        "realty_type_id": 3,
        "latest": False,
        "page": 1,
        "page_ads_number": 5,
        "operation_type_id": 3
     },
     {
        "price": {
            "ge": 10000,
            "le": 14000
        },
        "realty_type_id": 4,
        "latest": False,
        "page": 1,
        "page_ads_number": 4,
        "operation_type_id": 1
     },
     {
        "price": {
            "ge": 5000,
            "le": 13000
        },
        "realty_type_id": 2,
        "latest": False,
        "page": 1,
        "page_ads_number": 10,
        "operation_type_id": 1
     },
     ])
def test_for_getting_realties(filters, database, open_testing_data):
    """
    Test route for getting realties from database
    """
    with flask_app.test_request_context():
        with patch("service_api.client_api.resources.request.get_json") as mock_request:
            mock_request.return_value = filters
            mock_request.called_once()
            actual = RealtyResource().post()
            expected = filter_test_data(filters, open_testing_data)
            assert expected.sort(key=lambda x: x.get("id")) == actual.sort(key=lambda x: x.get("id"))


@patch("service_api.client_api.resources.get_latest_data_from_grabbing")
def test_for_getting_latest_realty(mock_grabbing_request, database):
    """
    Test route for getting latest realty from database
    """
    realty_data = {
        "id": 16,
        "city_id": 7,
        "state_id": 3,
        "realty_details_id": 8,
        "realty_type_id": 4,
        "operation_type_id": 3,
        "service_id": 1
    }
    realty_details_data = {
        "id": 16,
        "price": 1000.0,
        "published_at": "2020-08-16T12:27:01",
        "original_url": "https//url.to.realty.on.originals_site8"
    }
    realty_template = get_realty_template(realty_data, realty_details_data)
    with flask_app.test_request_context():
        with patch("service_api.client_api.resources.request.get_json") as mock_request:
            mock_request.return_value = {
                "price": {
                    "ge": 1000,
                    "le": 20000
                },
                "realty_type_id": 1,
                "latest": True,
                "page": 1,
                "page_ads_number": 1,
                "operation_type_id": 1
            }
            mock_grabbing_request.return_value = [realty_template]
            mock_grabbing_request.get_json.called_once()
            actual = RealtyResource().post()
            expected = [realty_template]
            assert expected.sort(key=lambda x: x.get("id")) == actual.sort(key=lambda x: x.get("id"))
