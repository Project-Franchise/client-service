"""
Client Api testing module
"""
from unittest.mock import patch

import pytest

from service_api import session, Base, engine, flask_app
from service_api.client_api.resources import StateResource, StatesResource, \
    CityResource, RealtyTypeResource, RealtyTypesResource, \
    OperationTypeResource, OperationTypesResource
from service_api.errors import BadRequestException
from service_api.models import State, RealtyType, OperationType, City


def setup_function():
    """
    Create all table and instances in DB
    """
    Base.metadata.create_all(engine)
    test_ids = [1, 2, 5, 10, 14]
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
        }
        operation_type_data = {
            "id": id_,
            "name": "TestOperationTypeName",
            "self_id": id_ + 1,
        }
        state, realty_type = State(**state_data), RealtyType(**realty_type_data)
        operation_type = OperationType(**operation_type_data)
        session.add(state)
        session.add(realty_type)
        session.add(operation_type)
    session.commit()
    for id_ in test_ids:
        city_data = {
            "id": id_ + 2,
            "name": "TestCityName" + str(id_ + 2),
            "state_id": id_ + 1,
            "self_id": id_ + 5
        }
        city = City(**city_data)
        session.add(city)
    session.commit()


def teardown_function():
    """
    Closes session if its open and drop database
    """
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
