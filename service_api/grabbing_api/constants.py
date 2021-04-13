"""
Constants for grabbing module
"""

import os

DOMRIA_DOMAIN: str = "https://developers.ria.com/dom"

DOMRIA_TOKEN = os.environ["DOMRIA_API_KEY"]
CACHED_CHARACTERISTICS = "characteristics_avaliable"
CACHED_CITIES = "cities_upload"
CACHED_STATES = "states_upload"

# must be dict with datetime.timedelta params
CACHED_CHARACTERISTICS_EXPIRE_TIME = {
    "days": 2
}

PATH_TO_METADATA = os.sep.join(["service_api", "static_data", "metadata.json"])
