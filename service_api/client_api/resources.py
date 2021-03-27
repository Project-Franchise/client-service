from flask_restful import Resource
from service_api import api_, Session, models, schemas
from contextlib import contextmanager
from flask import jsonify


Chars = {
    'Location': {
        'State': [1, 2, 3, 4],
        'City': [1, 2, 3, 4]
    },
    'Realty': {
        'floor': {
            'from': 'number',
            'to': 'number'
        },
        'floors_number': {
            'from': 'number',
            'to': 'number'
        },
        'square': {
            'from': 'number',
            'to': 'number'
        },
        'rental_price': {
            'from': 'number',
            'to': 'number'
        },
        'sale_price': {
            'from': 'number',
            'to': 'number'
        },
        'building_state': 'string'
    }
}


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


class Cities(Resource):
    def get(self, state_id):
        with session_scope() as session:
            session = Session()
            cities = session.query(models.City).filter_by(state_id=state_id).all()
        return jsonify(schemas.CitySchema(many=True).dump(cities))


class Characteristics(Resource):
    def get(self):

        return Chars


api_.add_resource(IndexResource, "/")
api_.add_resource(Cities, '/cities/<state_id>')
