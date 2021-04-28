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

GE = "from"
LE = "to"

PATH_TO_METADATA = os.sep.join(["service_api", "static_data", "metadata.json"])
PATH_TO_CORE_DB_METADATA = os.sep.join(["service_api", "static_data", "metadata_for_fetching_db_core.json"])

PATH_TO_OPERATION_TYPE_CSV = os.sep.join(["service_api", "static_data", "operation_type.csv"])
PATH_TO_OPERATION_TYPE_ALIASES_CSV = os.sep.join(["service_api", "static_data", "operation_type_aliases.csv"])

PATH_TO_REALTY_TYPE_CSV = os.sep.join(["service_api", "static_data", "realty_type.csv"])
PATH_TO_REALTY_TYPE_ALIASES_CSV = os.sep.join(["service_api", "static_data", "realty_type_aliases.csv"])

PATH_TO_SERVICES_CSV = os.sep.join(["service_api", "static_data", "services.csv"])

PATH_TO_STATE_CSV = os.sep.join(["service_api", "static_data", "states.csv"])
PATH_TO_STATE_ALIASES_CSV = os.sep.join(["service_api", "static_data", "state_aliases.csv"])

PATH_TO_CITIES_CSV = os.sep.join(["service_api", "static_data", "cities.csv"])
PATH_TO_CITIES_ALIASES_CSV = os.sep.join(["service_api", "static_data", "city_aliases.csv"])

PATH_TO_TRIGGERS_SQL = os.sep.join(["service_api", "static_data", "sql", "triggers.sql"])
