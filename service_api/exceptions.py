"""
Custom exceptions for service_api
"""


class BaseCustomException(Exception):
    """
    Base class for class custom exceptions
    """

    def __init__(self, message, desc="No decription provided") -> None:
        super().__init__(message)
        self.desc = desc


class ResponseNotOkException(BaseCustomException):
    """
    Exception shoud be raised when wen response from external service is not OK (status code ≥ 400)
    """
    ...


class ObjectNotFoundException(BaseCustomException):
    """
    Exception which should be used when sqlaclhemy returns None from get function
    """

    def __init__(self, message="Object not found", *args, **kwargs) -> None:
        super().__init__(message, *args, **kwargs)


class ModelNotFoundException(BaseCustomException):
    """
    Exception which should be used when sqlaclhemy returns None from get function
    """

    def __init__(self, message="Model not found", *args, **kwargs) -> None:
        super().__init__(message, *args, **kwargs)


class CycleReferenceException(BaseCustomException):
    """
    Raised when there is a cycle in dependencies
    """
    ...

class BadFiltersException(BaseCustomException):
    """
    Raised when there is a problem in filters
    """
    ...

class MetaDataError(BaseCustomException):
    """
    Raised when there is some problems with metadata
    """

    def __init__(self, *args, message="Metadata error occured", **kwargs) -> None:
        super().__init__(message, *args, **kwargs)


class AlreadyInDbException(BaseCustomException):
    """
    Raised when data is already in Db
    """

    def __init__(self, *args, message="Already in db", **kwargs) -> None:
        super().__init__(message, *args, **kwargs)

class LimitBoundError(BaseCustomException):
    """
    Raised when limit bound is reached
    """
