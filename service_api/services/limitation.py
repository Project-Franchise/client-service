"""
Limitation system module
"""

from ..constants import (PATH_TO_PARSER_METADATA, PATH_TO_METADATA)

from ..utils import open_metadata
from ..utils.patterns import Singleton
from .domria.limitation import DomriaLimitationSystem


class LimitationSystem(metaclass=Singleton):
    """
    Control number of request to services
    """
    SERVICES = {"DOMRIA API": DomriaLimitationSystem}

    def __init__(self) -> None:
        self.metadata = open_metadata(PATH_TO_METADATA) | open_metadata(PATH_TO_PARSER_METADATA)

    def mark_token_after_request(self, url: str):
        """
        Check if such url must be supervised and if so then mark it as used
        """
        for service in self.metadata.values():
            if url.startswith(service["base_url"]):
                self.SERVICES[service["name"]].mark_token_after_requset(url)
                break
