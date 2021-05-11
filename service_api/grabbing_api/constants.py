"""
Constants for grabbing module
"""

import os

DOMRIA_TOKEN = os.environ["DOMRIA_API_KEY"]
CACHED_CHARACTERISTICS = "characteristics_avaliable"
CACHED_CITIES = "cities_upload"
CACHED_STATES = "states_upload"

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
