from flask_restful import Resource
from . import api_

class indexClass(Resource):
    def get(self):
        return {'Project': 'Franchise'}

api_.add_resource(indexClass, '/')