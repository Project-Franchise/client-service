from marshmallow import Schema, fields
from pprint import pprint


class RealtySchema(Schema):

    id = fields.Integer()
    location_id = fields.Integer()
    floor = fields.Integer()
    square = fields.Integer()
    rental_price = fields.Float()
    sale_price = fields.Float()
    building_state = fields.String()
    published_at = fields.DateTime()
    original_id = fields.Integer()
    original_url = fields.Integer()
    realty_type_id = fields.Integer()
    operation_type_id = fields.Integer()


class OperationTypeSchema(Schema):

    id = fields.Integer()
    original_id = fields.Integer()
    name = fields.String()
    realty = fields.Integer()


class RealtyTypeSchema(Schema):

    id = fields.Integer()
    original_id = fields.Integer()
    name = fields.String()
    realty = fields.Integer()


class LocationSchema(Schema):

    id = fields.Integer()
    city_id = fields.Integer()
    street_name = fields.String()
    building_number = fields.Integer()
    realty = fields.Integer()


class CitySchema(Schema):

    id = fields.Integer()
    name = fields.String()
    state_id = fields.Integer()
    original_id = fields.Integer()
    location = fields.Integer()


class StateSchema(Schema):

    id = fields.Integer()
    name = fields.String()
    state_id = fields.Integer()
    original_id = fields.Integer()
    city = fields.Integer()


