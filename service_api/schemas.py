"""
Schemas for models with fields validation
"""
from datetime import datetime
from typing import Dict, List

from marshmallow import Schema, ValidationError, fields, validate

from service_api import Base
from service_api.constants import PARSING_REQUEST
from service_api.errors import BadRequestException


class IntOrDictField(fields.Field):
    """
    Custom field for validating int or dict elements
    """

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, (float, int)):
            return value

        if isinstance(value, dict) and value.get("to") and value.get("from"):
            return value

        raise ValidationError("Field should be int or dict with 'to' and 'from' keys")

    def _validate(self, value):
        if isinstance(value, dict):
            return super()._validate(value.get("to")), super()._validate(value.get("from"))
        return super()._validate(value)


def validate_non_negative_field(value):
    """
    Function for validation of positive fields
    """
    if value < 0:
        raise ValidationError("This field must be non negative")


def parsing_request(params):
    """
    Parse and convert input params to dict representation
    """
    params = list(params.getlist("filter"))
    new_params = {}
    for items in params:
        characteristic, operation, value = items.split()
        if operation not in PARSING_REQUEST.keys():
            raise BadRequestException("Wrong parameters operations")
        if PARSING_REQUEST[operation] is not None:
            if characteristic not in new_params.keys():
                new_params[characteristic] = {PARSING_REQUEST[operation]: int(value)}
            else:
                new_params[characteristic][PARSING_REQUEST[operation]] = int(value)
        else:
            new_params[characteristic] = int(value)
    return new_params


class OperationTypeSchema(Schema):
    """
    Schema for OperationType model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    self_id = fields.Integer(validate=validate_non_negative_field, required=True)


class AdditionalFilterParametersSchema(Schema):
    """
    Schema for additional filter parameters
    """
    page = fields.Integer(validate=validate_non_negative_field, required=True)
    page_ads_number = fields.Integer(validate=validate_non_negative_field, required=True)


class RealtyTypeSchema(Schema):
    """
    Schema for RealtyType model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    self_id = fields.Integer(validate=validate_non_negative_field, required=True)


class RealtyDetailsSchema(Schema):
    """
    Schema for RealtyDetails model
    """
    id = fields.Integer()
    floor = fields.Integer(validate=validate.Range(
        min=0, max=50), allow_none=True)
    floors_number = fields.Integer(
        validate=validate.Range(min=1, max=50), allow_none=True)
    square = fields.Float(validate=validate_non_negative_field, allow_none=True)
    price = fields.Float(validate=validate_non_negative_field, allow_none=True)
    published_at = fields.DateTime(validate=validate.Range(min=datetime(1990, 1, 1)))
    original_url = fields.String(validate=validate.Length(max=255))


class RealtyDetailsInputSchema(Schema):
    """
    Schema for RealtyDetails input
    """
    id = fields.Integer()
    floor = fields.Integer(validate=validate.Range(
        min=0, max=50), allow_none=True)
    floors_number = fields.Integer(
        validate=validate.Range(min=1, max=50), allow_none=True)
    square = fields.Dict(allow_none=True)
    price = fields.Dict(allow_none=True)
    published_at = fields.DateTime(validate=validate.Range(min=datetime(1990, 1, 1)))
    original_url = fields.String(validate=validate.Length(max=255))


class CitySchema(Schema):
    """
    Schema for City model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    state_id = fields.Integer(load_only=True)
    self_id = fields.Integer(validate=validate_non_negative_field, required=True)


class StateSchema(Schema):
    """
    Schema for State model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    self_id = fields.Integer(validate=validate_non_negative_field, required=True)


class RealtySchema(Schema):
    """
    Schema for Realty model
    """
    id = fields.Integer()
    city_id = fields.Integer(load_only=True, required=False)
    city = fields.Nested(CitySchema, dump_only=True)
    state_id = fields.Integer(load_only=True)
    state = fields.Nested(StateSchema, dump_only=True)
    realty_details_id = fields.Integer(load_only=True)
    realty_details = fields.Nested(RealtyDetailsSchema, dump_only=True)
    realty_type_id = fields.Integer(load_only=True, required=True)
    realty_type = fields.Nested(RealtyTypeSchema, dump_only=True)
    operation_type_id = fields.Integer(load_only=True, required=True)
    operation_type = fields.Nested(OperationTypeSchema, dump_only=True)


class ServiceSchema(Schema):
    """
    Schema for Service model
    """
    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))


class CityToServiceSchema(Schema):
    """
    Schema for CityToService model
    """
    city_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class CityAliasSchema(Schema):
    """
    Schema for CityAlias model
    """
    city_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


class StateToServiceSchema(Schema):
    """
    Schema for StateToService model
    """
    state_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class StateAliasSchema(Schema):
    """
    Schema for StateAlias model
    """
    state_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


class OperationTypeToServiceSchema(Schema):
    """
    Schema for OperationTypeToService model
    """
    operation_type_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class OperationTypeAliasSchema(Schema):
    """
    Schema for OperationTypeAlias model
    """
    operation_type_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


class RealtyTypeToServiceSchema(Schema):
    """
    Schema for RealtyTypeToService model
    """
    realty_type_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class RealtyTypeAliasSchema(Schema):
    """
    Schema for RealtyTypeAlias model
    """
    realty_type_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


def filters_validation(params: Dict, models: List[Base], schemes: List[Schema]) -> List[Dict]:
    """
    Method that validates filters for Realty and Realty_details
    :param: dict
    :return: List[dict]
    """
    filters = []
    for objects in models:

        filters.append({key: params.get(key)
                        for key in params
                        if hasattr(objects, key) or
                        (isinstance(objects, list) and key in objects)})

    if sum(map(len, filters)) != len(params):
        raise BadRequestException("Undefined parameters found")
    iter_filters = iter(filters)
    for scheme in schemes:
        dict_to_validate = next(iter_filters)
        try:
            scheme().load(dict_to_validate)
        except ValidationError as error:
            raise BadRequestException from error
    return filters
