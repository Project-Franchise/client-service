"""
Schemas for models with fields validation
"""
from datetime import datetime
from re import T

from marshmallow import Schema, ValidationError, fields, post_load, validate
from service_api.errors import BadRequestException
from .constants import ADDITIONAL_FILTERS
from service_api.models import (City, OperationType, Realty, RealtyDetails,
                                RealtyType, State)


def validate_positive_field(value):
    """
    Function for validation of positive fields
    """
    if value <= 0:
        raise ValidationError("This field must be non negative")


class OperationTypeSchema(Schema):
    """
    Schema for OperationType model
    """
    id = fields.Integer()
    original_id = fields.Integer(validate=validate_positive_field)
    name = fields.String(validate=validate.Length(max=255))


class AdditionalFilterParametersSchema(Schema):
    """
    Schema for additional filter parameters
    """
    page = fields.Integer(validate=validate_positive_field)
    page_ads_number = fields.Integer(validate=validate_positive_field)


class RealtyTypeSchema(Schema):
    """
    Schema for RealtyType model
    """
    id = fields.Integer()
    original_id = fields.Integer(validate=validate_positive_field)
    name = fields.String(validate=validate.Length(max=255))


class RealtyDetailsSchema(Schema):
    """
    Schema for RealtyDetails model
    """
    id = fields.Integer()
    floor = fields.Integer(validate=validate.Range(min=0, max=50), allow_none=True)
    floors_number = fields.Integer(validate=validate.Range(min=1, max=50), allow_none=True)
    square = fields.Integer(validate=lambda val: val >= 0,
                            error_messages={"validator_failed": "Square must be greater than 0"}, allow_none=True)
    price = fields.Float(validate=lambda val: val >= 0,
                         error_messages={"validator_failed": "Price must be greater than 0"})
    published_at = fields.DateTime(validate=validate.Range(min=datetime(1990, 1, 1)))
    original_id = fields.Integer(validate=validate_positive_field)
    original_url = fields.String(validate=validate.Length(max=255))


class CitySchema(Schema):
    """
    Schema for City model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    state_id = fields.Integer(load_only=True)
    original_id = fields.Integer(validate=validate_positive_field)


class StateSchema(Schema):
    """
    Schema for State model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    original_id = fields.Integer(validate=validate_positive_field)


class RealtySchema(Schema):
    """
    Schema for Realty model
    """
    id = fields.Integer()
    city_id = fields.Integer(load_only=True)
    city = fields.Nested(CitySchema, dump_only=True)
    state_id = fields.Integer(load_only=True)
    state = fields.Nested(StateSchema, dump_only=True)
    realty_details_id = fields.Integer(load_only=True)
    realty_details = fields.Nested(RealtyDetailsSchema, dump_only=True)
    realty_type_id = fields.Integer(load_only=True)
    realty_type = fields.Nested(RealtyTypeSchema, dump_only=True)
    operation_type_id = fields.Integer(load_only=True)
    operation_type = fields.Nested(OperationTypeSchema, dump_only=True)


def FiltersValidation(params):
    """
    Method that validates filters for Realty and Realty_details
    :param: dict
    :return: List[dict]
    """
    params_check, list_of_filters = [Realty, RealtyDetails, ADDITIONAL_FILTERS], []
    schemes = [RealtySchema, RealtyDetailsSchema, AdditionalFilterParametersSchema]
    for objects in params_check:
        filter_dict = {}
        counter = 0
        for key in params:
            if hasattr(objects, key) or (isinstance(objects, list) and key in objects):
                filter_dict[key] = params.get(key)
            else:
                counter += 1
        if counter == len(params_check):
            raise BadRequestException("Invalid input data!")
        list_of_filters.append(filter_dict)
    iter_list = iter(list_of_filters)
    for scheme in schemes:
        dict_to_validate = next(iter_list)
        try:
            validation = scheme().load(dict_to_validate)
        except ValidationError:
            raise BadRequestException("Validation failed!")
    return list_of_filters
