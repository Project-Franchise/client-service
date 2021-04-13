"""
Constans for grabbing module
"""

import os

from service_api.models import (City, OperationType, RealtyDetails, RealtyType,
                                State)

DOMRIA_DOMAIN: str = "https://developers.ria.com/dom"


DOMRIA_URL = {
    "cities": "/cities",
    "states": "/states",
    "options": "/options",
    "search": "/search",
    "id": "/info"
}

REALTY_KEYS = [
    ("city_id", City, "city_id"),
    ("state_id", State, "state_id"),
    ("realty_details_id", RealtyDetails, "realty_id"),
    ("realty_type_id", RealtyType, "realty_type_id"),
    ("operation_type_id", OperationType, "advert_type_id")

]

REALTY_DETAILS_KEYS = {
    "floor": "floor",
    "floors_number": "floors_count",
    "square": "total_square_meters",
    "price": "price",
    "published_at": "publishing_date",
    "original_id": "realty_id",
    "original_url": "beautiful_url",
}

REALTY_KEYS_FOR_REQUEST = [
    ("city_id", City, "city_id"),
    ("state_id", State, "state_id"),
    ("realty_type_id", RealtyType, "realty_type"),
    ("operation_type_id", OperationType, "operation_type")

]

DOMRIA_UKR = 4
DOMRIA_API_KEY = os.environ["DOMRIA_API_KEY"]
CACHED_CHARACTERISTICS = "characteristics_avaliable"
CACHED_CITIES = "number_of_cities_by_state"
CACHED_STATES = "number_of_states"

# must be dict with datetime.timedelta params
CACHED_CHARACTERISTICS_EXPIRE_TIME = {
    "days": 2
}
