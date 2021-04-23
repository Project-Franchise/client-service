"""
Constants for grabbing module
"""

import os

domria_keys_list = os.environ.get("DOMRIA_API_KEYS").split(".")
DOMRIA_TOKEN = domria_keys_list[0]
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
