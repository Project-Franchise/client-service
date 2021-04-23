"""
Utilities for cashing requests and saving them in redis
"""
import datetime
import json
from typing import Dict

from service_api import CACHE
from service_api.constants import CACHED_REQUESTS_EXPIRE_TIME


def make_hash(request_data: Dict, response_data: Dict, redis_ex_time: Dict = CACHED_REQUESTS_EXPIRE_TIME):
    """
    Hash request to redis
    """
    CACHE.set(str(hash(json.dumps(request_data, sort_keys=True))), json.dumps(response_data),
              datetime.timedelta(**redis_ex_time))


def get_hash(request_data: Dict):
    """
    Get hashed request from redis
    """
    return CACHE.get(str(hash(json.dumps(request_data, sort_keys=True))))
