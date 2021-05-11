"""
Utils module
"""
from requests import Session

from service_api import LOGGER


def send_request(method: str, url: str, request_session: Session = None, *args, **kwargs):
    """
    Wrapper for sending requests
    """
    LOGGER.info("Pre-request method")

    request_session = request_session or Session()
    return request_session.request(method, url, *args, **kwargs)
