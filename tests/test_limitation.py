"""
Limitation testing module
"""
from hashlib import sha256
from unittest.mock import Mock, PropertyMock, patch

import pytest
from service_api import Base, engine, session_scope
from service_api.exceptions import LimitBoundError
from service_api.models import RequestsHistory
from service_api.services.domria.limitation import DomriaLimitationSystem
from service_api.services.limitation import LimitationSystem

URL = "https://developers.ria.com/dom/search?api_key=token&param=1"


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


def test_limitation_signleton():
    """
    Checking if limitation follows singleton pattern
    """
    with patch("service_api.services.limitation.open_metadata") as mocked_open_metadata:
        mocked_open_metadata.return_value = {}
    firtst_instance = LimitationSystem()
    second_instance = LimitationSystem()

    assert id(firtst_instance) == id(second_instance)
    assert firtst_instance == second_instance


@patch("service_api.services.limitation.open_metadata")
@patch.object(LimitationSystem, "SERVICES")
def test_limitation_token_marking(mock_services, mock_open_metadata):
    """
    Checking if LimitationSystem marks tokens based on url
    """

    mock_services.return_value = {"DOMRIA API": Mock()}
    mock_open_metadata.return_value = {"DOMRIA API": {"name": "DOMRIA API",
                                                      "base_url": "https://developers.ria.com/dom"}}

    limitation = LimitationSystem()
    limitation.mark_token_after_request(URL)
    LimitationSystem.SERVICES["DOMRIA API"].mark_token_after_requset.assert_called_once_with(URL)


@pytest.mark.parametrize(("tokens", "expected"),
                         ((["token1", "token2"], "token1"),
                          (["secret token", "admin"], "secret token")))
def test_domria_limitation_get_token(tokens, expected):
    """
    Checking token getting from doria limitation system

    Table RequestHistory should be empty!!!
    """
    with patch.object(DomriaLimitationSystem, "TOKENS", tokens):
        assert DomriaLimitationSystem.get_token() == expected


@patch.object(DomriaLimitationSystem, "TOKENS", new_callable=PropertyMock)
def test_domria_limitation_token_marking(patch_tokens):
    """
    Checking if request is added to DB
    """
    patch_tokens.return_value = ["token"]
    url = "https://developers.ria.com/dom/search?api_key=token&param=1"
    DomriaLimitationSystem.mark_token_after_requset(url)

    with session_scope() as session:
        record = session.query(RequestsHistory).order_by(RequestsHistory.id.desc()).first()

    assert record.url == "https://developers.ria.com/dom/search?param=1"
    assert record.hashed_token == sha256("token".encode("utf-8")).hexdigest()


@pytest.mark.parametrize(("token_limit", "tokens", "tokens_till_error"),
                         ((10, ["token"], 10),
                          (10, ["token1", "token2"], 20),
                          (10, ["token1", "token2", "token3"], 30)))
def test_domria_limitation(token_limit, tokens, tokens_till_error):
    """
    Checking if DomriaLimitationSystem get_token is switching tokens and in the end raises error
    """
    with patch.object(DomriaLimitationSystem, "TOKEN_LIMIT", new_callable=PropertyMock) as patch_token_limit:
        patch_token_limit.return_value = token_limit
        with patch.object(DomriaLimitationSystem, "TOKENS", new_callable=PropertyMock) as patch_tokens:
            patch_tokens.return_value = tokens.copy()

            for i in range(tokens_till_error):
                assert DomriaLimitationSystem.get_token() == tokens[i//token_limit]
                DomriaLimitationSystem.mark_token_after_requset(URL)

            with pytest.raises(LimitBoundError):
                DomriaLimitationSystem.get_token()
