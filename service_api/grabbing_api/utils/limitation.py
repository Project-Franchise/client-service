"""
Limitation system module
"""
from datetime import datetime, timedelta
from hashlib import sha256

from marshmallow.exceptions import ValidationError

from service_api import LOGGER, session_scope
from service_api.exceptions import LimitBoundError
from service_api.grabbing_api.constants import DOMRIA_TOKENS_LIST
from service_api.models import RequestsHistory
from service_api.schemas import RequestsHistorySchema


class DomriaLimitationSystem:
    """
    Logic for limitation of requests to domria
    """
    TOKENS = DOMRIA_TOKENS_LIST
    TOKEN_LIMIT = 80
    EXPIRE_TIME = {
        "hours": 1,
        "minutes": 1
    }

    @classmethod
    def mark_token_after_requset(cls, url):
        """
        Add record to RequestHistory with hased token
        """
        request_schema = RequestsHistorySchema()

        try:
            valid_data = request_schema.load(
                {"url": url, "hashed_token": sha256(cls.TOKENS[0].encode("utf-8")).hexdigest()})
        except ValidationError as error:
            LOGGER.error("During logging requests: %s", error.normalized_messages())

        with session_scope() as session:
            record = RequestsHistory(**valid_data)
            session.add(record)

    @classmethod
    def get_token(cls) -> str:
        """
        Returns token or raise LimitBoundError
        """
        for token in range(2):
            token = cls.TOKENS[0]
            with session_scope() as session:
                hashed_token = sha256(token.encode("utf-8")).hexdigest()
                tmp = session.query(RequestsHistory).where(RequestsHistory.hashed_token == str(hashed_token) and
                                                           RequestsHistory.request_timestamp.between(
                    datetime.now() - timedelta(**cls.EXPIRE_TIME),
                    datetime.now())).count()

            if tmp < cls.TOKEN_LIMIT:
                return token

            cls.TOKENS.append(cls.TOKENS.pop(0))

        raise LimitBoundError("DOMRIA limit reached! Try later!")
