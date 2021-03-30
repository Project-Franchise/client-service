<<<<<<< HEAD
from marshmallow import Schema, fields, post_load
=======
from marshmallow import Schema, fields, post_load, validate
>>>>>>> main
from service_api.models import State, City, OperationType, Realty, \
    RealtyDetails, RealtyType


class OperationTypeSchema(Schema):

    id = fields.Integer()
    original_id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))

    @post_load
    def create_state(self, data, **kwargs):
        return OperationType(**data)


class RealtyTypeSchema(Schema):

    id = fields.Integer()
    original_id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))

    @post_load
    def create_state(self, data, **kwargs):
        return RealtyType(**data)


class RealtyDetailsSchema(Schema):

    id = fields.Integer()
    floor = fields.Integer()
    floors_number = fields.Integer()
    square = fields.Integer()
    price = fields.Float()
    published_at = fields.DateTime()
    original_id = fields.Integer()
<<<<<<< HEAD
    original_url = fields.String(validate=validate.Length(max=255))
=======
    original_url = fields.String()
>>>>>>> APIRoutes

    @post_load
    def create_state(self, data, **kwargs):
        return RealtyDetails(**data)


class CitySchema(Schema):

    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    state_id = fields.Integer()
    original_id = fields.Integer()

    @post_load
    def create_state(self, data, **kwargs):
        return City(**data)


class StateSchema(Schema):

    id = fields.Integer()
    name = fields.String(validate=validate.Length(max=255))
    original_id = fields.Integer()

    @post_load
    def create_state(self, data, **kwargs):
        return State(**data)


<<<<<<< HEAD
class LocationSchema(Schema):
=======
class RealtySchema(Schema):
>>>>>>> main

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
<<<<<<< HEAD
    def create_state(self, data):
        # return Location(**data)
        pass
=======
    def create_state(self, data, **kwargs):
        return Realty(**data)
>>>>>>> main
