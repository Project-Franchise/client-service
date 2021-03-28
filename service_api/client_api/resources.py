from flask_restful import Resource
<<<<<<< Updated upstream
from redis.exceptions import ConnectionError
from service_api import api_, cache
=======
<<<<<<< Updated upstream
from service_api import api_
=======
from redis.exceptions import ConnectionError
from service_api import api_, CACHE
>>>>>>> Stashed changes
>>>>>>> Stashed changes


class IndexResource(Resource):
    """Main View entity based on Resource(from flask_restful"""

    def get(self):
<<<<<<< Updated upstream
=======
<<<<<<< Updated upstream
        return "Project Realty"
=======
>>>>>>> Stashed changes
        """HTTP GET method realisation.
        :return: str
        """
        try:
<<<<<<< Updated upstream
            count = cache.incr('hits')
        except ConnectionError as exc:
            return f"Redis connection error {exc}"
        return f"Project Realty: hits: {count}"
=======
            count = CACHE.incr('hits')
        except ConnectionError as exc:
            return f"Redis connection error {exc}"
        return f"Project Realty: hits: {count}"
>>>>>>> Stashed changes
>>>>>>> Stashed changes


api_.add_resource(IndexResource, "/")
