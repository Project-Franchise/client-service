"""
Api routes for client api
"""

import requests
from flask import request
from flask_restful import Resource
from redis.exceptions import ConnectionError

from service_api import CACHE, api_, models, schemas, session_scope
from service_api.constants import URLS
from service_api.errors import BadRequestException, ServiceUnavailableException
from service_api.models import Realty, RealtyDetails
from service_api.schemas import FiltersValidation, RealtySchema


class IndexResource(Resource):
    """
    Main View entity based on Resource(from flask_restful
    """
    def get(self):
        """
        HTTP GET method realisation.
        :return: str
        """
        try:
            count = CACHE.incr("hits")
        except ConnectionError as exc:
            return f"Redis connection error {exc}"
        return f"Project Realty: hits: {count}"


class CityResource(Resource):
    """
    Route to retrieve city/cities by state and/or city id
    """

    def get(self):
        """
        Method that returns city/cities by state and/or city id
        :params: int, int
        :return: json(schema)
        """
        filters = request.args

        if not filters:
            raise BadRequestException("No filters provided")

        if errors := schemas.CitySchema().validate(filters):
            raise BadRequestException(errors)

        with session_scope() as session:
            city = session.query(models.City).filter_by(**filters).all()
        return schemas.CitySchema(many=True).dump(city), 200


class StatesResource(Resource):

    def get(self):
        """
        Method that returns list of all available states
        :param:
        :return: json(schema)
        """
        with session_scope() as session:
            states = session.query(models.State).all()
        return schemas.StateSchema(many=True).dump(states), 200


class StateResource(Resource):
    """
    Route to retrieve a particular state by id
    """

    def get(self, state_id):
        """
        Method that returns a particular state by id
        :param: int
        :return: json(schema)
        """
        with session_scope() as session:
            state = session.query(models.State).filter_by(id=state_id).first()
        return schemas.StateSchema().dump(state), 200


class RealtyResource(Resource):
    """
    Route to retrieve a list of realty from database or grabbing
    depending on "latest" flag
    """

    def post(self):
        """
        Method that retrieves a list of realty from database or grabbing
        :param: json
        :return: json(schema)
        """
        filters = request.get_json()
        if not filters:
            raise BadRequestException("No filters provided")
        try:
            latest = filters.pop("latest")
        except KeyError:
            raise BadRequestException("Flag latest not provided")

        realty_dict, realty_details_dict, additional_params_dict = FiltersValidation(filters)

        if latest:
            response = requests.post(
                "http://127.0.0.1:5000/grabbing/latest", json=filters)
            if response.status_code >= 400:
                raise ServiceUnavailableException("GRABBING does not respond")
            return response.json(), 200

        with session_scope() as session:

            realty = session.query(Realty).filter_by(**realty_dict).filter(
                *[
                    getattr(RealtyDetails, key).between(value["from"], value["to"])
                    if isinstance(value, dict)
                    else getattr(RealtyDetails, key) == value
                    for key, value in realty_details_dict.items()
                  ]
            ).join(RealtyDetails).all()

            return RealtySchema(many=True).dump(realty)


class RealtyTypesResource(Resource):
    """
    Route to retrieve all realty types
    """

    def get(self):
        """
        Method that retrieves all realty types
        :param:
        :return: json(schema)
        """
        with session_scope() as session:
            realty_types = session.query(models.RealtyType).all()
        return schemas.RealtyTypeSchema(many=True).dump(realty_types), 200


class RealtyTypeResource(Resource):
    """
    Route to retrieve realty type by realty type id
    """

    def get(self, realty_type_id):
        """
        Method that retrieves realty type by realty type id
        :param: int
        :return: json(schema)
        """
        with session_scope() as session:
            realty_type = session.query(models.RealtyType).filter_by(
                id=realty_type_id).first()
        return schemas.RealtyTypeSchema().dump(realty_type), 200


class OperationTypesResource(Resource):
    """
    Route to retrieve all operation types
    """

    def get(self):
        """
        Method that retrieves all operation types
        :param:
        :return: json(schema)
        """
        with session_scope() as session:
            operation_types = session.query(
                models.OperationType).filter_by().all()
        return schemas.OperationTypeSchema(many=True).dump(operation_types), 200


class OperationTypeResource(Resource):
    """
    Route to retrieve operation type by operation type id
    """

    def get(self, operation_type_id):
        """
        Method that retrieves operation type by operation type id
        :param: int
        :return: json(schema)
        """
        with session_scope() as session:
            operation_type = session.query(models.OperationType).filter_by(
                id=operation_type_id).first()
        return schemas.OperationTypeSchema().dump(operation_type), 200


api_.add_resource(IndexResource, URLS["CLIENT"]["INDEX_URL"])
api_.add_resource(CityResource, URLS["CLIENT"]["GET_CITIES_URL"])
api_.add_resource(RealtyResource, URLS["CLIENT"]["GET_REALTY_URL"])
api_.add_resource(StatesResource, URLS["CLIENT"]["GET_STATES_URL"])
api_.add_resource(StateResource, URLS["CLIENT"]["GET_STATES_BY_ID_URL"])
api_.add_resource(RealtyTypesResource, URLS["CLIENT"]["GET_REALTY_TYPES_URL"])
api_.add_resource(RealtyTypeResource, URLS["CLIENT"]["GET_REALTY_TYPE_BY_ID_URL"])
api_.add_resource(OperationTypesResource, URLS["CLIENT"]["GET_OPERATION_TYPES_URL"])
api_.add_resource(OperationTypeResource, URLS["CLIENT"]["GET_OPERATION_TYPE_BY_ID_URL"])
