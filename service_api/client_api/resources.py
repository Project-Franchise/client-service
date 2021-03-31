"""
Api routes for client api
"""
from flask_restful import Resource
from service_api import api_, Session, models, schemas
from contextlib import contextmanager
from typing import Iterator
from sqlalchemy.exc import SQLAlchemyError
from flask import request
import requests
from errors import BadRequestException, ServiceUnavailableException


@contextmanager
def session_scope() -> Iterator[Session]:
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    else:
        try:
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise


class IndexResource(Resource):
    """
    Route for resource indexing
    """
    def get(self):
        return "Project Realty"


class CityResource(Resource):
    """
    Route to retrieve city by state and/or city id
    """
    def get(self):
        filters = request.args
        if not filters:
            raise BadRequestException('No filters provided')
        with session_scope() as session:
            city = session.query(models.City).filter_by(**filters).all()
        return schemas.CitySchema(many=True).dump(city), 200


class StatesResource(Resource):
    def get(self):
        with session_scope() as session:
            states = session.query(models.State).filter_by().all()
        return schemas.StateSchema(many=True).dump(states), 200


class StateResource(Resource):
    def get(self, id):
        with session_scope() as session:
            state = session.query(models.State).filter_by(id=id).first()
        return schemas.StateSchema().dump(state), 200


class RealtyResource(Resource):
    """
    Route to retrieve a list of realty from database or grabbing
    depending on 'latest' flag
    """
    def post(self):
        filters = request.get_json()
        if not filters:
            raise BadRequestException('No filters provided')
        try:
            latest = filters.pop('latest')
        except KeyError:
            raise BadRequestException('Flag latest not provided')
        if latest:
            response = requests.get('', params=filters)
            if response.status_code == 503:
                raise ServiceUnavailableException('DOMRIA does not respond')
            return response.json(), 200
        else:
            realty_schema = schemas.RealtySchema()
            if errors := realty_schema.validate(filters):
                raise BadRequestException(errors)
            with session_scope() as session:
                realty = session.query(models.Realty).\
                    join(models.RealtyDetails).filter_by(**filters).all()
            return realty_schema.dump(realty, many=True), 200


class RealtyTypesResource(Resource):
    def get(self):
        with session_scope() as session:
            realty_types = session.query(models.RealtyType).filter_by().all()
        return schemas.RealtyTypeSchema(many=True).dump(realty_types), 200


class RealtyTypeResource(Resource):
    def get(self, realty_type_id):
        with session_scope() as session:
            realty_type = session.query(models.RealtyType).filter_by(id=realty_type_id).first()
        return schemas.RealtyTypeSchema().dump(realty_type), 200


class OperationTypesResource(Resource):
    def get(self):
        with session_scope() as session:
            operation_types = session.query(models.OperationType).filter_by().all()
        return schemas.OperationTypeSchema(many=True).dump(operation_types), 200


class OperationTypeResource(Resource):
    def get(self, operation_type_id):
        with session_scope() as session:
            operation_type = session.query(models.OperationType).filter_by(id=operation_type_id).first()
        return schemas.OperationTypeSchema().dump(operation_type), 200


api_.add_resource(IndexResource, "/")
api_.add_resource(CityResource, '/cities')
api_.add_resource(RealtyResource, '/realty')
api_.add_resource(StatesResource, '/states/')
api_.add_resource(StateResource, '/states/<id>')
api_.add_resource(RealtyTypesResource, '/realty_types/')
api_.add_resource(RealtyTypeResource, '/realty_type/<realty_type_id>')
api_.add_resource(OperationTypesResource, '/operation_types/')
api_.add_resource(OperationTypeResource, '/operation_type/<operation_type_id>')
