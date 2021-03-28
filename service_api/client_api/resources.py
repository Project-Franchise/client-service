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


api_.add_resource(IndexResource, "/")
api_.add_resource(Cities, '/cities/<state_id>')
api_.add_resource(City, '/cities/<state_id>/<id>')
api_.add_resource(Realty, '/realty')
api_.add_resource(RealtyByState, '/realty/<state_id>')
api_.add_resource(RealtyByCity, '/realty/<state_id>/<city_id>')
api_.add_resource(States, '/states/')
api_.add_resource(State, '/states/<id>')
