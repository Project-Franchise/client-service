import os

DOMRIA_DOMAIN = "https://developers.ria.com/dom"
DOMRIA_URL = {
    "cities": "/cities",
    "states": "/states",
    "options": "/options",
    "search": "/search",
    "id": "/info"
}
DOMRIA_UKR = 4
DOMRIA_API_KEY = os.environ["DOMRIA_API_KEY"]
REDIS_CITIES_FETCHED = "cities_upload"
REDIS_STATES_FETCHED = "states_upload"
