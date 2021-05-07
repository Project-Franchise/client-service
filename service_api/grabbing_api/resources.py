"""
Resources and urls for grabbing service
"""

from flask import request
from flask_restful import Resource
from service_api import api_
from service_api.constants import URLS
from service_api.errors import InternalServerErrorException
from service_api.exceptions import MetaDataError

from .utils.db import RealtyFetcher


class LatestDataResource(Resource):
    """
    Resource that is responsible for manipulation with latest data from resources described on metadata
    """

    def post(self):
        """
        Returns latest information about realty and save it to DB
        """

        post_body = request.get_json()
        try:
            fetcher = RealtyFetcher(post_body)
        except MetaDataError as error:
            raise InternalServerErrorException() from error

        return fetcher.fetch()

api_.add_resource(LatestDataResource, URLS["GRABBING"]["GET_LATEST_URL"])
