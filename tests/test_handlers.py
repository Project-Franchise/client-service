"""
Service handlers test module
"""

from hashlib import sha256
from unittest.mock import Mock, PropertyMock, patch

import pytest
from service_api import Base, engine, session_scope
from service_api.services.domria.handlers import DomriaServiceHandler
from service_api.services.olx.handlers import OlxServiceHandler
from service_api.exceptions import MetaDataError, ServiceHandlerError
from service_api.utils import open_metadata
from service_api.constants import (PATH_TO_METADATA, PATH_TO_PARSER_METADATA)
from copy import deepcopy

filters = {
    "realty_filters": {
        "realty_type_id": 3,
        "operation_type_id": 2
    },
    "characteristics": {
        "price": {
            "ge": 23000,
            "le": 44000
        }
    },
    "additional": {
        "page": 1,
        "page_ads_number": 10
    }
}


def setup_function():
    """
    Create all table and instances in DB
    """
    # sql_session.begin()
    Base.metadata.create_all(engine)


def teardown_function():
    """
    Closes sql_session if its open and drop database
    """
    with session_scope() as session:
        session.close()
        Base.metadata.drop_all(engine)


def test_domria_handler_key_error():
    with pytest.raises(MetaDataError):
        DomriaServiceHandler({"urls": {"search": 1}}, {"urls": {"search": 1}}).get_latest_data()


def test_domria_handler_responce_status_code():
    with patch('service_api.services.domria.handlers.send_request') as patched_request, \
            patch("service_api.services.domria.handlers.DomRiaInputConverter.convert") as mock_request:
        type(patched_request.return_value).status_code = PropertyMock(return_value=300)
        mock_request().return_value = {'realty_type': '5', 'operation_type': '3', 'characteristic[234][from]': 23000,
                                       'characteristic[234][to]': 44000, 'lang_id': 4, 'page': 1}
        with pytest.raises(ServiceHandlerError):
            DomriaServiceHandler(filters, open_metadata(PATH_TO_METADATA)["DOMRIA API"]).get_latest_data()


def test_domria_handler_second_key_error():
    with patch('service_api.services.domria.handlers.send_request') as patched_request, \
            patch("service_api.services.domria.handlers.DomRiaInputConverter.convert") as mock_request:
        type(patched_request.return_value).status_code = PropertyMock(return_value=200)
        mock_request.json.return_value = {'count': 0, 'items': []}
        mock_request().return_value = {'realty_type': '5', 'operation_type': '3', 'characteristic[234][from]': 23000,
                                       'characteristic[234][to]': 44000, 'lang_id': 4, 'page': 1}
        filter_copy = deepcopy(filters)
        filter_copy['additional'].pop('page')
        with pytest.raises(ServiceHandlerError):
            DomriaServiceHandler(filter_copy, open_metadata(PATH_TO_METADATA)["DOMRIA API"]).get_latest_data()


def test_olx_handler_amount_of_urls():
    with patch("service_api.services.olx.handlers.OLXOutputConverter.make_url") as mock_request, \
            patch("service_api.services.olx.handlers.OlxParser.main_logic") as mock_parser:
        mock_parser.main_logic.return_value = 1
        mock_request.return_value = "https://www.olx.ua/uk/nedvizhimost/doma/arenda-domov/dom/?search[filter_float_price:from]=33000&search[filter_float_price:to]=44000"
        assert len(OlxServiceHandler(filters, open_metadata(PATH_TO_PARSER_METADATA)
                                     ["OLX"]).get_latest_data()) == filters['additional']['page_ads_number']
