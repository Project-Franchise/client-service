from marshmallow import Schema, fields, post_load
from service_api.models import State, City, OperationType, Realty, \
    RealtyDetails, RealtyType


class OperationTypeSchema(Schema):

    id = fields.Integer()
    original_id = fields.Integer()
    name = fields.String()

    @post_load
    def create_state(self, data, **kwargs):
        return OperationType(**data)


class RealtyTypeSchema(Schema):

    id = fields.Integer()
    original_id = fields.Integer()
    name = fields.String()

    @post_load
    def create_state(self, data, **kwargs):
        return RealtyType(**data)


class RealtySchema(Schema):

    id = fields.Integer()
    location = fields.Nested()
    floor = fields.Integer()
    floors_number = fields.Integer()
    square = fields.Integer()
    rental_price = fields.Float()
    sale_price = fields.Float()
    building_state = fields.String()
    published_at = fields.DateTime()
    original_id = fields.Integer()
    original_url = fields.Integer()
    realty_type_id = fields.Integer()
    realty_type = fields.Nested(RealtyTypeSchema)
    operation_type_id = fields.Integer()
    operation_type = fields.Nested(OperationTypeSchema)

    @post_load
    def create_state(self, data, **kwargs):
        return Realty(**data)


class StateSchema(Schema):

    id = fields.Integer()
    name = fields.String()
    original_id = fields.Integer()

    @post_load
    def create_state(self, data, **kwargs):
        return State(**data)


class CitySchema(Schema):

    id = fields.Integer()
    name = fields.String()
    original_id = fields.Integer()
    state_id = fields.Integer()
    state = fields.Nested(StateSchema)

    @post_load
    def create_state(self, data, **kwargs):
        return City(**data)


class LocationSchema(Schema):

    id = fields.Integer()
    street_name = fields.String()
    building_number = fields.Integer()
    city_id = fields.Integer()
    city = fields.Nested(CitySchema)

    @post_load
    def create_state(self, data):
        # return Location(**data)
        pass
