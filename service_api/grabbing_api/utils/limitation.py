"""
Limitation system module
"""
from datetime import datetime, timedelta

from service_api import LOGGER, session_scope
from service_api.exceptions import AlreadyInDbException, LimitBoundError
from service_api.grabbing_api.constants import DOMRIA_TOKENS_LIST
from service_api.models import RequestsHistory
from service_api.schemas import RequestsHistorySchema

from .grabbing_utils import load_data


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
        try:
            load_data(RequestsHistorySchema(), {"url": url, "hashed_token": str(hash(cls.TOKENS[0]))},
                      RequestsHistory)
        except AlreadyInDbException as error:
            LOGGER.error("Fail during creating Domria history record: %s", error.args)

    @classmethod
    def get_token(cls) -> str:
        """
        Returns token or raise LimitBoundError
        """
        for token in range(2):
            token = cls.TOKENS[0]
            with session_scope() as session:
                hashed_token = hash(token)
                tmp = session.query(RequestsHistory).where(RequestsHistory.hashed_token == str(hashed_token) and
                                                           RequestsHistory.request_timestamp.between(
                    datetime.now() - timedelta(**cls.EXPIRE_TIME),
                    datetime.now())).count()

            if tmp < cls.TOKEN_LIMIT:
                return token

            cls.TOKENS.append(cls.TOKENS.pop(0))

        raise LimitBoundError("DOMRIA limit reached! Try later!")
