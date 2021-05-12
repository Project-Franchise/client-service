"""
Schemas for models with fields validation
"""
from datetime import datetime
from typing import Dict, List, Tuple

from marshmallow import Schema, ValidationError, fields, validate

from service_api import Base
from service_api.constants import PARSING_REQUEST
from service_api.errors import BadRequestException
from service_api.exceptions import BadFiltersException


def validate_non_negative_field(value):
    """
    Function for validation of positive fields
    """
    if value < 0:
        raise ValidationError("This field must be non negative")


def validate_range_filters(value):
    """
    Function for validation of range filters
    """
    if value.get("le") and value.get("ge") and value.get("le") < value.get("ge"):
        raise ValidationError("Invalid range parameters")


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
    category_id = fields.Integer(load_only=True)
    self_id = fields.Integer(validate=validate_non_negative_field, required=True)


class CategorySchema(Schema):
    """
    Schema for Category model
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
    floor = fields.Dict(allow_none=True)
    floors_number = fields.Dict(allow_none=True)
    square = fields.Dict(allow_none=True)
    price = fields.Dict(allow_none=True)
    published_at = fields.DateTime(validate=validate.Range(min=datetime(1990, 1, 1)))
    original_url = fields.String(validate=validate.Length(max=255))
    version = fields.String()


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
    operation_type_id = fields.Integer(load_only=True)
    operation_type = fields.Nested(OperationTypeSchema, dump_only=True)
    version = fields.String()
    service_id = fields.Integer(load_only=True)


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
    entity_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class CityAliasSchema(Schema):
    """
    Schema for CityAlias model
    """
    entity_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


class StateToServiceSchema(Schema):
    """
    Schema for StateToService model
    """
    entity_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class StateAliasSchema(Schema):
    """
    Schema for StateAlias model
    """
    entity_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


class OperationTypeToServiceSchema(Schema):
    """
    Schema for OperationTypeToService model
    """
    entity_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class OperationTypeAliasSchema(Schema):
    """
    Schema for OperationTypeAlias model
    """
    entity_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


class RealtyTypeToServiceSchema(Schema):
    """
    Schema for RealtyTypeToService model
    """
    entity_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class RealtyTypeAliasSchema(Schema):
    """
    Schema for RealtyTypeAlias model
    """
    entity_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


class CategoryToServiceSchema(Schema):
    """
    Schema for CategoryToService model
    """
    entity_id = fields.Integer()
    service_id = fields.Integer()
    original_id = fields.String(validate=validate.Length(max=255))


class CategoryAliasSchema(Schema):
    """
    Schema for CategoryAlias model
    """
    entity_id = fields.Integer()
    alias = fields.String(validate=validate.Length(max=255))


class RequestsHistorySchema(Schema):
    """
    Schema for Requests History
    """
    id = fields.Integer()
    url = fields.String(validate=validate.Length(max=4096))
    hashed_token = fields.String(validate=validate.Length(max=255))
    request_timestamp = fields.DateTime(
        validate=validate.Range(min=datetime(1990, 1, 1)))


def filters_validation(params: Dict, validators: List[Tuple[Base, Schema]]) -> List[Dict]:
    """
    Method that validates filters for Realty and Realty_details
    :param: dict
    :return: List[dict]
    """
    models, schemes = zip(*validators)
    filters = [{key: params.get(key) for key in params if hasattr(objects, key)} for objects in models]

    if sum(map(len, filters)) != len(params):
        raise BadFiltersException("Undefined parameters found")
    iter_filters = iter(filters)

    for item in filters:
        item = {key: values for key, values in item.items() if isinstance(values, dict)}

    for scheme in schemes:
        dict_to_validate = next(iter_filters)
        try:
            scheme().load(dict_to_validate)
        except ValidationError as error:
            raise BadFiltersException("Filters validation error. Bad filters", desc=error.args) from error
    return filters
