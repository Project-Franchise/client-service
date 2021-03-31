from flask_restful import Resource
from redis.exceptions import ConnectionError
from service_api import CACHE, api_


class IndexResource(Resource):
    """Main View entity based on Resource(from flask_restful"""

    def get(self):
        """HTTP GET method realisation.
        :return: str
        """
        try:
            count = CACHE.incr("hits")
        except ConnectionError as exc:
            return f"Redis connection error {exc}"
        return f"Project Realty: hits: {count}"


api_.add_resource(IndexResource, "/")
