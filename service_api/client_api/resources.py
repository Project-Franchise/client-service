from flask_restful import Resource
from service_api import api_, Session, models, schemas
from contextlib import contextmanager


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    else:
        try:
            session.commit()
        except:
            session.rollback()
            raise


class IndexResource(Resource):
    def get(self):
        return "Project Realty"


class City(Resource):
    def get(self, state_id, id):
        with session_scope() as session:
            session = Session()
            city = session.query(models.City).filter_by(state_id=state_id, id=id).first()
        return schemas.CitySchema().dump(city)


class Cities(Resource):
    def get(self, state_id):
        with session_scope() as session:
            session = Session()
            cities = session.query(models.City).filter_by(state_id=state_id).all()
        return schemas.CitySchema(many=True).dump(cities)


class States(Resource):
    def get(self):
        with session_scope() as session:
            session = Session()
            states = session.query(models.State).filter_by().all()
        return schemas.StateSchema(many=True).dump(states)


class State(Resource):
    def get(self, id):
        with session_scope() as session:
            session = Session()
            state = session.query(models.State).filter_by(id=id).first()
        return schemas.StateSchema().dump(state)


class Realty(Resource):
    def get(self):
        with session_scope() as session:
            session = Session()
            realties = session.query(models.Realty).filter_by().all()
        return schemas.RealtySchema(many=True).dump(realties)


class RealtyByCity(Resource):
    def get(self, state_id, city_id):
        with session_scope() as session:
            session = Session()
            realties = session.query(models.Realty).filter_by(state_id=state_id, city_id=city_id).all()
        return schemas.RealtySchema(many=True).dump(realties)


class RealtyByState(Resource):
    def get(self, state_id):
        with session_scope() as session:
            session = Session()
            realties = session.query(models.Realty).filter_by(state_id=state_id).all()
        return schemas.RealtySchema(many=True).dump(realties)


class RealtyDetails(Resource):
    def get(self, realty_details_id):
        with session_scope() as session:
            session = Session()
            realty = session.query(models.Realty).filter_by(realty_details_id=realty_details_id).first()
            details = session.query(models.RealtyDetails).filter_by(id=realty.realty_details_id).first()
        return schemas.RealtyDetailsSchema().dump(details)


class RealtyTypes(Resource):
    def get(self):
        with session_scope() as session:
            session = Session()
            realty_types = session.query(models.RealtyType).filter_by().all()
        return schemas.RealtyTypeSchema(many=True).dump(realty_types)


class RealtyType(Resource):
    def get(self, realty_type_id):
        with session_scope() as session:
            session = Session()
            realty_type = session.query(models.RealtyType).filter_by(id=realty_type_id).first()
        return schemas.RealtyTypeSchema().dump(realty_type)


class OperationTypes(Resource):
    def get(self):
        with session_scope() as session:
            session = Session()
            operation_types = session.query(models.OperationType).filter_by().all()
        return schemas.OperationTypeSchema(many=True).dump(operation_types)


class OperationType(Resource):
    def get(self, operation_type_id):
        with session_scope() as session:
            session = Session()
            operation_type = session.query(models.OperationType).filter_by(id=operation_type_id).first()
        return schemas.OperationTypeSchema().dump(operation_type)

api_.add_resource(IndexResource, "/")
api_.add_resource(Cities, '/cities/<state_id>')
api_.add_resource(City, '/cities/<state_id>/<id>')
api_.add_resource(Realty, '/realty')
api_.add_resource(RealtyByState, '/realty/<state_id>')
api_.add_resource(RealtyByCity, '/realty/<state_id>/<city_id>')
api_.add_resource(States, '/states/')
api_.add_resource(State, '/states/<id>')
api_.add_resource(RealtyDetails, '/details/<realty_details_id>')
api_.add_resource(RealtyTypes, '/realty_types/')
api_.add_resource(RealtyType, '/realty_type/<realty_type_id>')
api_.add_resource(OperationTypes, '/operation_types/')
api_.add_resource(OperationType, '/operation_type/<operation_type_id>')