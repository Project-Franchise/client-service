"""
Contains logic for comunication with external realty services
"""

from .domria.handlers import DomriaServiceHandler
from .olx.handlers import OlxServiceHandler

services_handlers = {
    "DomriaServiceHandler": DomriaServiceHandler,
    "OlxServiceHandler": OlxServiceHandler
}
