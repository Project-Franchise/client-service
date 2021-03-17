from flask_restful import Resource
from service_api import api_


class IndexResource(Resource):
    def get(self):
        return "Project Realty"


api_.add_resource(IndexResource, "/")