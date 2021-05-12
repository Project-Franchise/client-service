"""
Service_api global constants
"""
URLS = {
    "CLIENT": {
        "INDEX_URL": "/",
        "GET_CITIES_URL": "/cities",
        "GET_CITY_BY_ID_URL": "/city",
        "GET_REALTY_URL": "/realty",
        "GET_STATES_URL": "/states",
        "GET_STATES_BY_ID_URL": "/states/<state_id>",
        "GET_REALTY_TYPES_URL": "/realty_types",
        "GET_REALTY_TYPE_BY_ID_URL": "/realty_type/<realty_type_id>",
        "GET_OPERATION_TYPES_URL": "/operation_types",
        "GET_OPERATION_TYPE_BY_ID_URL": "/operation_type/<operation_type_id>"
    },
    "GRABBING": {
        "GET_CORE_DATA_URL": "/grabbing/core_data",
        "GET_LATEST_URL": "/grabbing/latest"
    }
}

CACHED_REQUESTS_EXPIRE_TIME = {
    "hours": 2
}

PARSING_REQUEST = {"le": "to", "ge": "from", "eq": None}
VERSION_DEFAULT_TIMESTAMP = None

PAGE_LIMIT = 10_000
CRONTAB_FILLING_DB_WITH_REALTIES_SCHEDULE = {
    "minute": "*/5"
}
