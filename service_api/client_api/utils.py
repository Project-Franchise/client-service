"""
Utilities for cashing requests and saving them in redis
"""
import datetime
import json
from typing import Dict, Union
from hashlib import sha256
import requests
from sqlalchemy.util.langhelpers import NoneType

from service_api import CACHE, LOGGER
from ..errors import ServiceUnavailableException
from ..constants import CACHED_REQUESTS_EXPIRE_TIME


def make_hash(request_data: Dict, response_data: Dict, redis_ex_time: Union[Dict, NoneType] = None):
    """
    Hash request to redis
    """
    CACHE.set(str(sha256(json.dumps(request_data, sort_keys=True).encode("utf-8")).hexdigest()),
              json.dumps(response_data), datetime.timedelta(**(redis_ex_time or CACHED_REQUESTS_EXPIRE_TIME)))


def get_hash(request_data: Dict):
    """
    Get hashed request from redis
    """
    return CACHE.get(str(sha256(json.dumps(request_data, sort_keys=True).encode("utf-8")).hexdigest()))


def get_latest_data_from_grabbing(request_filters: Dict, url: str):
    """
    Entrypoint to get latest data from grabbing or from cache
    """
    if cached_response := get_hash(request_filters):
        LOGGER.debug("___hashed stuff___")
        return json.loads(cached_response), 200
    response = requests.post(url, json=request_filters)
    if response.status_code >= 400:
        raise ServiceUnavailableException("GRABBING does not respond")
    result = response.json()
    if result:
        make_hash(request_filters, result)
    return result, 200
