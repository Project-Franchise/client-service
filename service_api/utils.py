"""
Utils module
"""
from requests import Session

from service_api.grabbing_api.utils.limitation import LimitationSystem


def send_request(method: str, url: str, request_session: Session = None, *args, **kwargs):
    """
    Wrapper for sending requests
    """
    request_session = request_session or Session()
    response = request_session.request(method, url, *args, **kwargs)
    LimitationSystem().mark_token_after_request(response.url)
    return response
