"""
Client Api testing module
"""
from unittest.mock import patch

import pytest

from service_api import Base, engine, flask_app, session_scope
from service_api.client_api.resources import StateResource, StatesResource, \
    CityResource, CitiesResource, RealtyTypeResource, RealtyTypesResource, \
    OperationTypeResource, OperationTypesResource, RealtyResource
from service_api.errors import BadRequestException
from service_api.models import State, RealtyType, OperationType, City, Category, Realty, RealtyDetails, Service


def fill_db_with_test_data():
    """
    Function for filling testing database
    """
    test_ids = [1, 2, 5, 10, 14]
    obj_container = []
    category1 = Category(id=1, name="test_category1", self_id=1)
    service1 = Service(id=1, name="TestService")
    for id_ in test_ids:
        state_data = {
            "id": id_,
            "name": "TestStateName",
            "self_id": id_ + 1,
        }
        realty_type_data = {
            "id": id_,
            "name": "TestRealtyTypeName",
            "self_id": id_ + 1,
            "category_id": 1
        }
        operation_type_data = {
            "id": id_,
            "name": "TestOperationTypeName",
            "self_id": id_ + 1,
        }
        obj_container.extend([
            State(**state_data),
            RealtyType(**realty_type_data),
            OperationType(**operation_type_data)
        ])
    with session_scope() as session:
        session.add(category1)
        session.add(service1)
        session.commit()
        session.add_all(obj_container)
        session.commit()
        obj_container.clear()
    for id_ in test_ids:
        city_data = {
            "id": id_ + 2,
            "name": "TestCityName" + str(id_ + 2),
            "state_id": id_,
            "self_id": id_ + 5
        }
        city = City(**city_data)
        obj_container.append(city)
    with session_scope() as session:
        session.add_all(obj_container)
        session.commit()
    realty_det_data = {
        "id": 1,
        "price": 5000,
        "published_at": "2015-08-07 05:00:01",
        "original_url": "https//url.to.realty.on.originals_site",
    }
    realty_data = {
        "id": 1,
        "city_id": 3,
        "state_id": 1,
        "realty_details_id": 1,
        "realty_type_id": 1,
        "operation_type_id": 1,
        "service_id": 1
    }
    realty_det1, realty1 = RealtyDetails(**realty_det_data), Realty(**realty_data)
    with session_scope() as session:
        session.add(realty_det1)
        session.commit()
        session.add(realty1)
        session.commit()

def setup_function():
    """
    Create all table and instances in DB
    """
    # sql_session.begin()
    Base.metadata.create_all(engine)
    fill_db_with_test_data()


def teardown_function():
    """
    Closes sql_session if its open and drop database
    """
    with session_scope() as session:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.mark.parametrize("state_id", [1, 2, 10, 5, 14])
def test_get_state_by_id(state_id):
    """
    Checking the db response of state model by id
    """
    actual, response_code = StateResource().get(state_id=state_id)
    expected = {"self_id": state_id + 1,
                "name": "TestStateName",
                "id": state_id}
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


def test_get_states():
    """
    Checking the db response of all state models
    """
    actual, response_code = StatesResource().get()
    expected = [{"self_id": 2, "name": "TestStateName", "id": 1},
                {"self_id": 3, "name": "TestStateName", "id": 2},
                {"self_id": 6, "name": "TestStateName", "id": 5},
                {"self_id": 11, "name": "TestStateName", "id": 10},
                {"self_id": 15, "name": "TestStateName", "id": 14},
                ]
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


def test_get_realty_types():
    """
    Checking the db response of all realty_types
    """
    actual, response_code = RealtyTypesResource().get()
    expected = [{"self_id": 2, "name": "TestRealtyTypeName", "id": 1},
                {"self_id": 3, "name": "TestRealtyTypeName", "id": 2},
                {"self_id": 6, "name": "TestRealtyTypeName", "id": 5},
                {"self_id": 11, "name": "TestRealtyTypeName", "id": 10},
                {"self_id": 15, "name": "TestRealtyTypeName", "id": 14},
                ]
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


@pytest.mark.parametrize("realty_type_id", [1, 2, 10, 5, 14])
def test_get_realty_type_by_id(realty_type_id):
    """
    Checking the db response of realty_type model by id
    """
    actual, response_code = RealtyTypeResource().get(realty_type_id=realty_type_id)
    expected = {"self_id": realty_type_id + 1,
                "name": "TestRealtyTypeName",
                "id": realty_type_id}
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


def test_get_operation_types():
    """
    Checking the db response of all operation_types
    """
    actual, response_code = OperationTypesResource().get()
    expected = [{"self_id": 2, "name": "TestOperationTypeName", "id": 1},
                {"self_id": 3, "name": "TestOperationTypeName", "id": 2},
                {"self_id": 6, "name": "TestOperationTypeName", "id": 5},
                {"self_id": 11, "name": "TestOperationTypeName", "id": 10},
                {"self_id": 15, "name": "TestOperationTypeName", "id": 14},
                ]
    expected_code = 200
    assert actual == expected
    assert response_code == expected_code


@pytest.mark.parametrize("operation_type_id", [1, 2, 10, 5, 14])
def test_get_operation_type_by_id(operation_type_id):
    """
    Checking the db response of operation type model by id
    """
    actual, response_code = OperationTypeResource().get(operation_type_id=operation_type_id)
    expected = {"self_id": operation_type_id + 1,
                "name": "TestOperationTypeName",
                "id": operation_type_id}
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
def test_get_cites_validate_exception(arguments, expected_exception):
    """
    Test route with validation method for exception
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
        "self_id": 19
     },
     {
        "id": 3,
        "self_id": 6
     },
     {
        "self_id": 7,
        "name": "TestCityName4"
     },
     {
        "state_id": 1,
        "self_id": 6
     },
     {
        "id": 12,
        "self_id": 15,
        "state_id": 10
     },
     {
        "id": 7,
        "self_id": 10,
        "name": "TestCityName7",
        "state_id": 5
     },
     {
        "self_id": 6,
        "name": "TestCityName3",
        "state_id": 1
     },
     {
        "id": 16,
        "name": "TestCityName16",
        "self_id": 19
     }])
def test_get_city_by_id(filters):
    """
    Test route for get city by id
    """
    with flask_app.test_request_context():
        with patch("service_api.client_api.resources.request") as mock_request:
            mock_request.args = filters
            actual, response_code = CityResource().get()
            expected = [{
                "id": filters["self_id"] - 3,
                "name": "TestCityName" + str(filters["self_id"] - 3),
                "self_id": filters["self_id"]
            }]
        expected_code = 200
        assert actual == expected
        assert response_code == expected_code


def test_get_cities():
    """
    Checking the db response of all cities
    """
    actual, response_code = CitiesResource().get()
    expected = [{"self_id": 6, "name": "TestCityName3", "id": 3},
                {"self_id": 7, "name": "TestCityName4", "id": 4},
                {"self_id": 10, "name": "TestCityName7", "id": 7},
                {"self_id": 15, "name": "TestCityName12", "id": 12},
                {"self_id": 19, "name": "TestCityName16", "id": 16},
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
      }, BadRequestException)])
def test_filter_validation_for_getting_city(filters, expected_exception):
    """
    Test route for getting realties from database
    """
    with flask_app.test_request_context():
        with patch("service_api.client_api.resources.request") as mock_request:
            mock_request.get_json().returned_value = filters
            mock_request.get_json().called_once()
            with pytest.raises(expected_exception):
                CityResource().get()


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
              "ge": 1000
          },
          "page_ads_number": 1,
          "latest": True,
          "state_id": 1,
          "realty_type_id": 1,
          "operation_type_id": 1
      }, BadRequestException),
     ])
def test_filter_validation_for_getting_realty(filters, expected_exception):
    """
    Test route for getting realties from database with validation method for exception
    """
    with flask_app.test_request_context():
        with patch("service_api.client_api.resources.request") as mock_request:
            mock_request.get_json().returned_value = filters
            mock_request.get_json().called_once()
            with pytest.raises(expected_exception):
                RealtyResource().post()
