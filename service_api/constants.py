"""
Service_api global constants
"""
import os

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
        "GET_LATEST_URL": "/grabbing/latest"
    }
}

CACHED_REQUESTS_EXPIRE_TIME = {
    "hours": 2
}


ADDITIONAL_FILTERS = ["page", "page_ads_number"]
PARSING_REQUEST = {"le": "le", "ge": "ge", "eq": None}
LE = 10**18
GE = 0
VERSION_DEFAULT_TIMESTAMP = None

PAGE_LIMIT = 10_000
CRONTAB_FILLING_DB_WITH_REALTIES_SCHEDULE = {
    "minute": "*/2"
}


DOMRIA_TOKENS_LIST = os.environ.get("DOMRIA_API_KEYS").split(".")
CACHED_CHARACTERISTICS = "characteristics_avaliable"

# must be dict with datetime.timedelta params
CACHED_CHARACTERISTICS_EXPIRE_TIME = {
    "days": 2
}

GE = "ge"
LE = "le"

path_to_static_data = ["service_api", "static_data"]

PATH_TO_METADATA = os.sep.join([*path_to_static_data, "new_metadata.json"])
PATH_TO_CORE_DB_METADATA = os.sep.join([*path_to_static_data, "metadata_for_fetching_db_core.json"])

PATH_TO_PARSER_METADATA = os.sep.join([*path_to_static_data, "parser_metadata.json"])

PATH_TO_OPERATION_TYPE_CSV = os.sep.join([*path_to_static_data, "operation_type.csv"])
PATH_TO_OPERATION_TYPE_ALIASES_CSV = os.sep.join([*path_to_static_data, "operation_type_aliases.csv"])

PATH_TO_REALTY_TYPE_CSV = os.sep.join([*path_to_static_data, "realty_type.csv"])
PATH_TO_REALTY_TYPE_ALIASES_CSV = os.sep.join([*path_to_static_data, "realty_type_aliases.csv"])

PATH_TO_CATEGORIES_CSV = os.sep.join([*path_to_static_data, "categories.csv"])
PATH_TO_CATEGORY_ALIASES_CSV = os.sep.join([*path_to_static_data, "category_aliases.csv"])

PATH_TO_SERVICES_CSV = os.sep.join([*path_to_static_data, "services.csv"])

PATH_TO_STATE_CSV = os.sep.join([*path_to_static_data, "states.csv"])
PATH_TO_STATE_ALIASES_CSV = os.sep.join([*path_to_static_data, "state_aliases.csv"])

PATH_TO_CITIES_CSV = os.sep.join([*path_to_static_data, "cities.csv"])
PATH_TO_CITIES_ALIASES_CSV = os.sep.join([*path_to_static_data, "city_aliases.csv"])

PATH_TO_PARSER_METADATA = os.sep.join([*path_to_static_data, "parser_metadata.json"])
