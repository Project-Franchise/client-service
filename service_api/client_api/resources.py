from flask_restful import Resource
from service_api import api_, cache
from redis.exceptions import ConnectionError


class IndexResource(Resource):
    def get(self):
        try:
            count = cache.incr('hits')
        except ConnectionError as exc:
            return f"Redis connection error {exc}"
        return f"Project Realty: hits: {count}"


api_.add_resource(IndexResource, "/")
