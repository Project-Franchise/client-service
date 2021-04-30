"""
Resources and urls for grabbing service
"""

from flask import request
from flask_restful import Resource

from service_api import api_
from service_api.constants import URLS
from service_api.errors import InternalServerErrorException
from service_api.exceptions import MetaDataError
from .constants import (PATH_TO_METADATA)
from .utils.db import RealtyLoadersFactory
from .utils.grabbing_utils import open_metadata
from .utils.services_handler import DomriaServiceHandler


class LatestDataResource(Resource):
    """
    Resource that is responsible for manipulation with latest data from resources described on metadata
    """

    def post(self):
        """
        Returns latest information about realty and save it to DB
        """

        post_body = request.get_json()
        metadata = open_metadata(PATH_TO_METADATA)
        for service_name in metadata:
            realty_service_metadata = metadata[service_name]
            request_to_domria = DomriaServiceHandler(post_body, realty_service_metadata)
            response = request_to_domria.get_latest_data()
            factory = RealtyLoadersFactory()
            try:
                factory.load(response)
            except MetaDataError as error:
                raise InternalServerErrorException() from error

            return response


api_.add_resource(LatestDataResource, URLS["GRABBING"]["GET_LATEST_URL"])
