"""
Custom exceptions for service_api
"""

class BaseCustomException(Exception):
    """
    Base class for class custom exceptions
    """

    def __init__(self, message, errors=None) -> None:
        super().__init__(message)
        self.errors = errors or []


class ResponseNotOk(BaseCustomException):
    """
    Exception shoud be raised when wen response from external service is not OK (status code ≥ 400)
    """
    ...


class ObjectNotFound(BaseCustomException):
    """
    Exception which should be used when sqlaclhemy returns None from get function
    """

    def __init__(self, message="Object not found", errors=None) -> None:
        super().__init__(message, errors)
