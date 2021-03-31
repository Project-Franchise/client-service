from flask import jsonify
from service_api import flask_app


class BadRequestException(Exception):

    def __init__(self, message='Bad request sent'):
        Exception.__init__(self)
        self.status_code = 400
        self.type = 'BAD_REQUEST'
        self.message = message

    def to_dict(self):
        resp = dict()
        resp['message'] = self.message
        resp['code'] = self.status_code
        resp['type'] = self.type
        return resp


class ServiceUnavailableException(Exception):

    def __init__(self, message='Service Unavailable'):
        Exception.__init__(self)
        self.status_code = 503
        self.type = 'Service_Unavailable_Error'
        self.message = message

    def to_dict(self):
        resp = dict()
        resp['message'] = self.message
        resp['code'] = self.status_code
        resp['type'] = self.type
        return resp


def handle_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def not_found(e):
    response = jsonify(code=404, type='NOT_FOUND', message='Not found')
    return response, 404


def internal_server_error(e):
    response = jsonify(code=500, type='INTERNAL_SERVER_ERROR', message='Internal Server Error')
    return response, 500


flask_app.register_error_handler(404, not_found)
flask_app.register_error_handler(500, internal_server_error)
flask_app.register_error_handler(BadRequestException, handle_error)
flask_app.register_error_handler(ServiceUnavailableException, handle_error)
