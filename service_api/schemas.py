"""
Schemas for models with fields validation
"""
from datetime import datetime
from typing import Dict, List

from marshmallow import Schema, ValidationError, fields, validate
from service_api.errors import BadRequestException
from service_api import Base

from service_api.models import (City, OperationType, Realty, RealtyDetails,
                                RealtyType, State)


class IntOrDictField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, (float, int)):
            return value
        elif isinstance(value, dict) and value.get("to") and value.get("from"):
            return value
        else:
            raise ValidationError("Field should be int or dict with 'to' and 'from' keys")

    def _validate(self, value):
        if isinstance(value, dict):
            return super()._validate(value.get("to")), super()._validate(value.get("from"))
        return super()._validate(value)


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
    page = fields.Integer(validate=validate_positive_field, required=True)
    page_ads_number = fields.Integer(validate=validate_positive_field, required=True)


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
    floor = fields.Integer(validate=validate.Range(
        min=0, max=50), allow_none=True)
    floors_number = fields.Integer(
        validate=validate.Range(min=1, max=50), allow_none=True)
    square = IntOrDictField(validate=validate_positive_field, allow_none=True)
    price = IntOrDictField(validate=validate_positive_field)
    published_at = fields.DateTime(
        validate=validate.Range(min=datetime(1990, 1, 1)))
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
    realty_type_id = fields.Integer(load_only=True, required=True)
    realty_type = fields.Nested(RealtyTypeSchema, dump_only=True)
    operation_type_id = fields.Integer(load_only=True, required=True)
    operation_type = fields.Nested(OperationTypeSchema, dump_only=True)


def filters_validation(params: Dict, list_of_models: List[Base], schemes: List[Schema]) -> List[Dict]:
    """
    Method that validates filters for Realty and Realty_details
    :param: dict
    :return: List[dict]
    """
    list_of_filters = []
    for objects in list_of_models:

        list_of_filters.append({key: params.get(key)
                                for key in params
                                if hasattr(objects, key) or
                                (isinstance(objects, list) and key in objects)})

    if sum(map(len, list_of_filters)) != len(params):
        raise BadRequestException("Undefinded parameters found")
    iter_list = iter(list_of_filters)
    for scheme in schemes:
        dict_to_validate = next(iter_list)
        try:
            scheme().load(dict_to_validate)
        except ValidationError as err:
            raise BadRequestException(err.args)
    return list_of_filters
