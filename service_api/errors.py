"""
Module to handle HTTP status codes
"""
from flask import jsonify

from service_api import flask_app


class BadRequestException(Exception):
    """
    Class for Bad Request Exception(400 status code)
    """

    def __init__(self, message="Bad request sent"):
        """
        Method to initialize bad request params(status_code, type, message)
        :param: string
        :return:
        """

        Exception.__init__(self)
        self.status_code = 400
        self.type = "BAD_REQUEST"
        self.message = message

    def to_dict(self):
        """
        Method that turns params into a dictionary
        :param: object itself
        :return: dict
        """

        resp = {
            "message": self.message,
            "code": self.status_code,
            "type": self.type
        }
        return resp


class ServiceUnavailableException(Exception):
    """
    Class for Service Unavailable Exception(503 status code)
    """

    def __init__(self, message="Service Unavailable"):
        """
        Method to initialize Service Unavailable Exception(status_code, type, message)
        :param: string
        :return:
        """

        Exception.__init__(self)
        self.status_code = 503
        self.type = "Service_Unavailable_Error"
        self.message = message

    def to_dict(self):
        """
        Method that turns params into a dictionary
        :param: object itself
        :return: dict
        """

        resp = {
            "message": self.message,
            "code": self.status_code,
            "type": self.type
        }
        return resp


class TooManyRequestsException(Exception):
    """
    Class for Too Many Requests Exception(429 status code)
    """

    def __init__(self, message="Too Many Requests"):
        """
        Method to initialize Too Many Requests Exception(status_code, type, message)
        :param: string
        :return:
        """

        Exception.__init__(self)
        self.status_code = 429
        self.type = "Too_Many_Requests"
        self.message = message

    def to_dict(self):
        """
        Method that turns params into a dictionary
        :param: object itself
        :return: dict
        """
        resp = {
            "message": self.message,
            "code": self.status_code,
            "type": self.type
        }
        return resp


class InternalServerErrorException(Exception):
    """
    Class for Internal Server Error(500 status code)
    """

    def __init__(self, message="Internal Server Error"):
        """
        Method to initialize Internal Server Error Exception(status_code, type, message)
        :param: string
        :return:
        """

        Exception.__init__(self)
        self.status_code = 500
        self.type = "Internal_server_error"
        self.message = message

    def to_dict(self):
        """
        Method that turns params into a dictionary
        :param: object itself
        :return: dict
        """
        resp = {
            "message": self.message,
            "code": self.status_code,
            "type": self.type
        }
        return resp


def handle_error(error):
    """
    Method that handles errors
    :return: json, status_code
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def not_found(error="Not found"):
    """
    Method that handles Not Found
    :return: json, status_code
    """
    response = jsonify(code=404, type="NOT_FOUND", message=error)
    return response, 404


def internal_server_error(error="Internal Server Error"):
    """
    Method that handles Internal Server Error
    :return: json, status_code
    """
    response = jsonify(code=500, type="INTERNAL_SERVER_ERROR", message=error)
    return response, 500


def conflict(error="Conflict"):
    """
    Method that handles Conflict
    :return: json, status_code
    """
    response = jsonify(code=409, type="CONFLICT", message=error)
    return response, 409


flask_app.register_error_handler(404, not_found)
flask_app.register_error_handler(500, internal_server_error)
flask_app.register_error_handler(409, conflict)
flask_app.register_error_handler(BadRequestException, handle_error)
flask_app.register_error_handler(ServiceUnavailableException, handle_error)
flask_app.register_error_handler(TooManyRequestsException, handle_error)
flask_app.register_error_handler(InternalServerErrorException, handle_error)
