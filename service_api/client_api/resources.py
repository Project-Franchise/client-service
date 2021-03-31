"""
Api routes for client api
"""
from flask_restful import Resource
from service_api import api_, Session, models, schemas, CACHE
from contextlib import contextmanager
from typing import Iterator
from sqlalchemy.exc import SQLAlchemyError
from flask import request
import requests


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
        """HTTP GET method realisation.
        :return: str
        """
        try:
            count = CACHE.incr("hits")
        except ConnectionError as exc:
            return f"Redis connection error {exc}"
        return f"Project Realty: hits: {count}"


class CityResource(Resource):
    """
    Route to retrieve city by state and city id
    """
    def get(self, state_id, city_id):
        with session_scope() as session:
            city = session.query(models.City).filter_by(state_id=state_id, id=city_id).first()
        return schemas.CitySchema().dump(city)


class CitiesResource(Resource):
    """
    Route to retrieve all cities in a particular state
    """
    def get(self, state_id):
        with session_scope() as session:
            cities = session.query(models.City).filter_by(state_id=state_id).all()
        return schemas.CitySchema(many=True).dump(cities)


class StatesResource(Resource):
    def get(self):
        with session_scope() as session:
            states = session.query(models.State).filter_by().all()
        return schemas.StateSchema(many=True).dump(states)


class StateResource(Resource):
    def get(self, id):
        with session_scope() as session:
            state = session.query(models.State).filter_by(id=id).first()
        return schemas.StateSchema().dump(state)


# bug: filters must be validated
class RealtyResource(Resource):
    """
    Route to retrieve a list of realty from database or grabbing
    depending on 'latest' flag
    """
    def post(self):
        filters = request.get_json()
        try:
            latest = filters.pop('latest')
        except KeyError:
            return {'error': 'flag latest not provided'}
        if latest:
            response = requests.get('', params=filters)
            return response.json()
        else:
            realty_schema = schemas.RealtySchema()
            if errors := realty_schema.validate(filters):
                return errors
            with session_scope() as session:
                realty = session.query(models.Realty).\
                    join(models.RealtyDetails).filter_by(**filters).all()
            return realty_schema.dump(realty, many=True)


class RealtyTypesResource(Resource):
    def get(self):
        filters = request.args
        if int(filters["id"]) < 0:
            return {'error': 'invalid id'}
        with session_scope() as session:
            realty_types = session.query(models.RealtyType).filter_by(**filters).all()
        return schemas.RealtyTypeSchema(many=True).dump(realty_types)


class RealtyTypeResource(Resource):
    def get(self, realty_type_id):
        with session_scope() as session:
            realty_type = session.query(models.RealtyType).filter_by(id=realty_type_id).first()
        return schemas.RealtyTypeSchema().dump(realty_type)


class OperationTypesResource(Resource):
    def get(self):
        with session_scope() as session:
            operation_types = session.query(models.OperationType).filter_by().all()
        return schemas.OperationTypeSchema(many=True).dump(operation_types)


class OperationTypeResource(Resource):
    def get(self, operation_type_id):
        with session_scope() as session:
            operation_type = session.query(models.OperationType).filter_by(id=operation_type_id).first()
        return schemas.OperationTypeSchema().dump(operation_type)


api_.add_resource(IndexResource, "/")
api_.add_resource(CitiesResource, '/cities/<state_id>')
api_.add_resource(CityResource, '/cities/<state_id>/<id>')
api_.add_resource(RealtyResource, '/realty')
api_.add_resource(StatesResource, '/states/')
api_.add_resource(StateResource, '/states/<id>')
api_.add_resource(RealtyTypesResource, '/realty_types/')
api_.add_resource(RealtyTypeResource, '/realty_type/<realty_type_id>')
api_.add_resource(OperationTypesResource, '/operation_types/')
api_.add_resource(OperationTypeResource, '/operation_type/<operation_type_id>')
