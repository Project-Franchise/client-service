"""
Resources and urls for grabbing service
"""

from flask import request
from flask_restful import Resource

from service_api import api_
from service_api.constants import URLS
from service_api.errors import InternalServerErrorException
from service_api.exceptions import MetaDataError
from .utils.services_handler import DomriaServiceHandler
from .constants import (PATH_TO_METADATA)
from .utils.db import LoadersFactory, RealtyLoadersFactory
from .utils.grabbing_utils import open_metadata


class CoreDataLoaderResource(Resource):
    """
    Resourse for fetching new core data to db
    """

    def get(self):
        """
        Load data to db based on input params

        Example of get request to load data to DB
            /grabbing/core_data?cities=144&states
        This request trigger fetching states and cities where state_id=144

        All possible entites to load is located in metadata_for_fetching_DB_core.json
        Only cities can take additional params that will be represented as a list.
            /grabbing/core_data?operation_types&cities=5&cities=144
        Here cities: [5, 144] and all cities from such states (if state exists) will be loaded.
        By default, if none parameters for city is passed, cities from ALL states will be loaded!!!
        """
        params = {key: list(filter(lambda x: x != "", value)) for key, value in request.args.to_dict(False).items()}
        factory = LoadersFactory()
        try:
            loading_statuses = factory.load(**params)
        except MetaDataError as error:
            raise InternalServerErrorException() from error
        return loading_statuses


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
            service_metadata = metadata[service_name]
            request_to_domria = DomriaServiceHandler(post_body, service_metadata)

            response = request_to_domria.get_latest_data()
            factory = RealtyLoadersFactory()

            try:
                factory.load(response)
            except MetaDataError as error:
                raise InternalServerErrorException() from error

            return response


api_.add_resource(CoreDataLoaderResource, URLS["GRABBING"]["GET_CORE_DATA_URL"])
api_.add_resource(LatestDataResource, URLS["GRABBING"]["GET_LATEST_URL"])
