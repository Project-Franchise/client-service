"""
Resources and urls for grabbing service
"""
from typing import Dict

from flask import request
from flask_restful import Resource
from service_api import api_, models, session_scope
from service_api.constants import URLS
from service_api.errors import BadRequestException, InternalServerErrorException
from service_api.grabbing_api.realty_requests import RealtyRequesterToServiceResource
from service_api.exceptions import MetaDataError
from .characteristics import process_characteristics
from .constants import (CACHED_CHARACTERISTICS, CACHED_CHARACTERISTICS_EXPIRE_TIME, PATH_TO_METADATA)
from .utils.db import LoadersFactory
from .utils.grabbing_utils import open_metadata, process_request


class CoreDataLoaderResource(Resource):
    """
    Resourse for fetching new core data to db
    """

    def get(self):
        """
        Load data to db based on input params
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

    @staticmethod
    def convert_named_filed(realty: Dict, service_metadata: Dict):
        """
        Convert fields names to service names and replace id for its api
        """
        params = {}
        with session_scope() as session:
            for param, characteristics in service_metadata["model_characteristics"]["realty_columns"].items():
                if not characteristics["request_key"]:
                    continue

                model = characteristics["model"]
                service_param = characteristics["request_key"]

                model = getattr(models, model)
                if not model:
                    raise Warning(f"There is no such model named {model}")

                if param in realty:
                    obj = session.query(model).get(realty[param])
                    if obj is None:
                        raise BadRequestException("No such filters!")
                    params[service_param] = obj.original_id
        return params

    def post(self):
        """
        Returns latest information about realty and save it to DB
        """

        post_body = request.get_json()

        try:
            characteristics = post_body["characteristics"]
            realty = post_body["realty_filters"]
            additional = post_body["additional"]
        except KeyError as error:
            raise BadRequestException(error.args) from error

        metadata = open_metadata(PATH_TO_METADATA)

        for service_name in metadata:
            service_metadata = metadata[service_name]
            params = self.convert_named_filed(realty, service_metadata)

            type_mapper = process_characteristics(service_metadata, realty, CACHED_CHARACTERISTICS_EXPIRE_TIME,
                                                  CACHED_CHARACTERISTICS)
            params.update(dict((type_mapper.get(key, key), {"name": key, "values": value})
                               for key, value in characteristics.items()))

            items = RealtyRequesterToServiceResource().get(params, service_metadata)
            try:
                return process_request(items, dict(additional).pop("page"), additional.pop("page_ads_number"),
                                       service_metadata)
            except KeyError as error:
                print(error.args)
                raise BadRequestException(error.args) from error


api_.add_resource(CoreDataLoaderResource, URLS["GRABBING"]["GET_CORE_DATA_URL"])
api_.add_resource(LatestDataResource, URLS["GRABBING"]["GET_LATEST_URL"])
