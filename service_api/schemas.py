"""
Schemas for models with fields validation
"""
from datetime import datetime

from marshmallow import Schema, ValidationError, fields, post_load, validate

from .constants import ADDITIONAL_FILTERS
from service_api.models import (City, OperationType, Realty, RealtyDetails,
                                RealtyType, State)


def FiltersValidation(params):
    """
    Method that validates filters for Realty and Realty_details
    :param: dict
    :return: List[dict]
    """
    realty_dict = dict()
    realty_details_dict = dict()
    additional_params_dict = dict()
    for key in params:
        if hasattr(Realty, key):
            realty_dict[key] = params.get(key)
        elif hasattr(RealtyDetails, key):
            realty_details_dict[key] = params.get(key)
        elif key in ADDITIONAL_FILTERS:
            additional_params_dict[key] = params.get(key)
        else:
            return "ERROR!"
    return [realty_dict, realty_details_dict, additional_params_dict]


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

    @post_load
    def create_state(self, data, **kwargs):
        """
        Post_load function for returning for OperationType model
        """
        return OperationType(**data)


class RealtyTypeSchema(Schema):
    """
    Schema for RealtyType model
    """
    id = fields.Integer()
    original_id = fields.Integer(validate=validate_positive_field)
    name = fields.String(validate=validate.Length(max=255))

    @post_load
    def create_state(self, data, **kwargs):
        """
        Post_load function for returning for RealtyType model
        """
        return RealtyType(**data)


class RealtyDetailsSchema(Schema):
    """
    Schema for RealtyDetails model
    """
    id = fields.Integer()
    floor = fields.Integer(validate=validate.Range(min=0, max=50))
    floors_number = fields.Integer(validate=validate.Range(min=1, max=50))
    square = fields.Integer(validate=lambda val: val >= 0,
                            error_messages={"validator_failed": "Square must be greater than 0"})
    price = fields.Float(validate=lambda val: val >= 0,
                         error_messages={"validator_failed": "Price must be greater than 0"})
    published_at = fields.DateTime(validate=validate.Range(min=datetime(1990, 1, 1)))
    original_id = fields.Integer(validate=validate_positive_field)
    original_url = fields.String(validate=validate.Length(max=255))

    @post_load
    def create_state(self, data, **kwargs):
        """
        Post_load function for returning for RealtyDetails model
        """
        return RealtyDetails(**data)


class CitySchema(Schema):
    """
    Schema for City model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    state_id = fields.Integer(load_only=True)
    original_id = fields.Integer(validate=validate_positive_field)

    @post_load
    def create_state(self, data, **kwargs):
        """
        Post_load function for returning for City model
        """
        return City(**data)


class StateSchema(Schema):
    """
    Schema for State model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    original_id = fields.Integer(validate=validate_positive_field)

    @post_load
    def create_state(self, data, **kwargs):
        """
        Post_load function for returning for State model
        """
        return State(**data)


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

    @post_load
    def create_state(self, data, **kwargs):
        """
        Post_load function for returning for Realty model
        """
        return Realty(**data)
