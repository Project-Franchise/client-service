from datetime import datetime

from marshmallow import Schema, fields, post_load, validate, ValidationError

from service_api.models import State, City, OperationType, Realty, \
    RealtyDetails, RealtyType


def validate_positive_field(value):
    if value <= 0:
        raise ValidationError("This field must be non negative")


class OperationTypeSchema(Schema):

    id = fields.Integer()
    original_id = fields.Integer(validate=validate_positive_field)
    name = fields.String(validate=validate.Length(max=255))

    @post_load
    def create_state(self, data, **kwargs):
        return OperationType(**data)


class RealtyTypeSchema(Schema):

    id = fields.Integer()
    original_id = fields.Integer(validate=validate_positive_field)
    name = fields.String(validate=validate.Length(max=255))

    @post_load
    def create_state(self, data, **kwargs):
        return RealtyType(**data)


class RealtyDetailsSchema(Schema):

    id = fields.Integer()
    floor = fields.Integer(validate=validate.Range(min=0, max=50))
    floors_number = fields.Integer(validate=validate.Range(min=1, max=50))
    square = fields.Integer(validate=lambda val: val >= 0,
                            error_messages={"validator_failed": "Square must be greater than 0"})
    price = fields.Float(validate=lambda val: val >= 0,
                         error_messages={"validator_failed": "Price must be greater than 0"})
    published_at = fields.DateTime(validate=validate.Range(min=datetime(1990, 1, 1), max=datetime.now()))
    original_id = fields.Integer(validate=validate_positive_field)
    original_url = fields.String(validate=validate.Length(max=255))

    @post_load
    def create_state(self, data, **kwargs):
        return RealtyDetails(**data)


class CitySchema(Schema):

    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    state_id = fields.Integer(load_only=True)
    original_id = fields.Integer(validate=validate_positive_field)

    @post_load
    def create_state(self, data, **kwargs):
        return City(**data)


class StateSchema(Schema):

    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    original_id = fields.Integer(validate=validate_positive_field)

    @post_load
    def create_state(self, data, **kwargs):
        return State(**data)


class RealtySchema(Schema):

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
        return Realty(**data)
