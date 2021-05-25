"""
Contains logic for comunication with external realty services
"""

from .domria.handlers import DomriaServiceHandler
from .domria.loaders import (DomriaCityXRefServicesLoader, DomriaStateXRefServicesLoader)
from .olx.handlers import OlxServiceHandler
from .olx.loaders import OlxCityXRefServicesLoader, OlxStateXRefServicesLoader

services_handlers = {
    "DomriaServiceHandler": DomriaServiceHandler,
    "OlxServiceHandler": OlxServiceHandler
}

state_loaders = {"DOMRIA API": DomriaStateXRefServicesLoader,
                 "OLX": OlxStateXRefServicesLoader}

city_loaders = {"DOMRIA API": DomriaCityXRefServicesLoader,
                "OLX": OlxCityXRefServicesLoader}
