from service_api import models

DOMRIA_DOMAIN = "https://developers.ria.com/dom"
PAGE_ADS_NUMBER = 10

DOMRIA_URL = {
    "cities": "/cities",
    "states": "/states",
    "options": "/options",
    "search": "/search",
    "id": "/info"
}

REALTY_KEYS = [
    ("city_id", models.City, "city_id"),
    ("state_id", models.State, "state_id"),
    ("realty_details_id", models.RealtyDetails, "realty_id"),
    ("realty_type_id", models.RealtyType, "realty_type_id"),
    ("operation_type_id", models.OperationType, "advert_type_id")

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


