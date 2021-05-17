"""
Async logic for making requests to Domria Api
"""
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List

import requests

from service_api.utils import send_request

thread_local = threading.local()


def get_session():
    """
    Get session if one already exists and make it local for thread
    :return: Session
    """
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def get_single_response(url, params, item_id):
    """
    Task to make a request to Domria API within a single thread
    :return: Response
    """
    session = get_session()
    return send_request("GET", url.format(id=str(item_id)), session, params=params,
                        headers={'User-Agent': 'Mozilla/5.0'})


def get_all_responses(url, params, id_container: List):
    """
    Main function to make requests to Domria API in parallel
    :return: List[Dict]
    """
    num = len(id_container)
    with ThreadPoolExecutor(max_workers=4) as executor:
        result = list(executor.map(get_single_response, [url] * num, [params] * num, id_container))
        executor.shutdown(wait=True)
    return result
