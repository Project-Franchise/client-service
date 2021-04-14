"""
Constants for grabbing module
"""

import os

DOMRIA_TOKEN = os.environ["DOMRIA_API_KEY"]
REDIS_CHARACTERISTICS = "characteristics_avaliable"
REDIS_CITIES_FETCHED = "cities_upload"
REDIS_STATES_FETCHED = "states_upload"

# must be dict with datetime.timedelta params
REDIS_CHARACTERISTICS_EX_TIME = {
    "hours": 2
}

PATH_TO_METADATA = os.sep.join(["service_api", "static_data", "metadata.json"])
GENERAL_CHARACTERISTICS = ["city_id"]
