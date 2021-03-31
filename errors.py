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


def handle_bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def not_found(e):
    response = jsonify(code=404, type='NOT_FOUND', message='Not found')
    return response, 404


flask_app.register_error_handler(404, not_found)
flask_app.register_error_handler(BadRequestException, handle_bad_request)
