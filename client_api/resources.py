from flask_restful import Resource
from . import api_


class IndexResource(Resource):
    def get(self):
        return "Project Realty"


api_.add_resource(IndexResource, "/")
