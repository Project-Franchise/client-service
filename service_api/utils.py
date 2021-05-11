"""
Utils module
"""
from requests import Session

from service_api.grabbing_api.utils.limitation import DomriaLimitationSystem


def send_request(method: str, url: str, request_session: Session = None, *args, **kwargs):
    """
    Wrapper for sending requests
    """
    request_session = request_session or Session()
    response = request_session.request(method, url, *args, **kwargs)
    DomriaLimitationSystem.mark_token_after_requset(response.url)
    return response
