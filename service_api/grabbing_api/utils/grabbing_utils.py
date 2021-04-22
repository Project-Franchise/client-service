"""
Utilities for creating models and saving them in DB
"""

import json
from functools import singledispatch
from typing import Dict, List, Union

import requests
from marshmallow import ValidationError
from marshmallow.schema import Schema
from service_api import Base, models, session_scope
from service_api.models import Realty, RealtyDetails
from service_api.errors import BadRequestException
from service_api.exceptions import AlreadyInDbException
from service_api.grabbing_api.constants import DOMRIA_TOKEN
from service_api.schemas import RealtyDetailsSchema, RealtySchema
import datetime

@singledispatch
def load_data(model_schema: Schema, data: Dict, model: Base) -> Base:
    """
    Stores data in a database according to a given scheme
    """
    try:
        valid_data = model_schema.load(data)
        record = model(**valid_data)
    except ValidationError as error:
        print(error)
        raise

    with session_scope() as session:
        session.add(record)
    return record

@load_data.register
def _(model_schema: RealtyDetailsSchema, data: Dict, model: RealtyDetails):
    try:
        valid_data = model_schema.load(data)
        realty_details_record = model(**valid_data)
        
    except ValidationError as error:
        print(error)
        raise
    with session_scope() as session:
        realty_details = session.query(model).filter_by(
            original_id=realty_details_record.original_id, version=realty_details_record.version).first()

    if realty_details is not None:
        print("version: ", realty_details.version)
        incoming_data = model_schema.dump(realty_details_record)
        db_data = model_schema.dump(realty_details)
        incoming_data.pop("id")
        db_data.pop("id")
        if incoming_data == db_data:
            raise AlreadyInDbException
        with session_scope() as session:
            print("they aren't equal")
            session.expire_on_commit = False
            session.query(model).filter_by(
                original_id=realty_details.original_id, version=realty_details.version).update(
                {"version": datetime.datetime.now()})

            session.add(realty_details_record)
            session.commit()
            realty_record = session.query(Realty).filter_by(
                realty_details_id=realty_details.id).first()
            new_realty_details_id = session.query(model).filter_by(
                original_id=realty_details_record.original_id, version=realty_details_record.version).first().id

            session.expunge(realty_record)
            del realty_record.id
            realty_record.realty_details_id = new_realty_details_id
            
            print("needed id: ", model_schema.dump(realty_details).get("id"))
            session.query(Realty).filter_by(
                realty_details_id=model_schema.dump(realty_details).get("id")).update(
                {"version": datetime.datetime.now()})
            
            session.add(realty_record)

        with session_scope() as session:
            session.query(Realty).filter_by(
                realty_details_id=model_schema.dump(realty_details).get("id")).update(
                {"version": datetime.datetime.now()})
    with session_scope() as session:
        session.add(realty_details_record)
    return realty_details_record


@load_data.register
def _(model_schema: RealtySchema, data: Dict, model: Realty):
    try:
        valid_data = model_schema.load(data)
        record = model(**valid_data)
        print("record.realty_details_id: ", record.realty_details_id)
    except ValidationError as error:
        print(error)
        # raise
    with session_scope() as session:
        stuff = session.query(model).filter_by(realty_details_id=record.realty_details_id,
                                               version=record.version).first()
        print("stuff: ", stuff)
    if stuff is not None:
        print("version: ", stuff.version)
        raise AlreadyInDbException
    with session_scope() as session:
        session.add(record)
    return record

def make_realty_details_data(response: requests.models.Response, realty_details_meta: Dict) -> Dict:
    """
    Composes data for RealtyDetails model
    """

    data = response.json()

    keys = realty_details_meta.keys()
    values = [data.get(val["response_key"], None) for val in realty_details_meta.values()]

    realty_details_data = dict(zip(
        keys, values
    ))

    return realty_details_data


def make_realty_data(response: requests.models.Response, realty_keys: Dict) -> Dict:
    """
    Composes data for Realty model
    """
    realty_data = {}
    with session_scope() as session:
        for key, characteristics in realty_keys.items():
            model = characteristics["model"]
            response_key = characteristics["response_key"]

            model = getattr(models, model)

            if not model:
                raise Warning(f"There is no such model named {model}")

            realty_data[key] = (session.query(model).filter(
                model.original_id == response.json()[response_key]
            ).first()).id  # and service_name == service_name

    return realty_data


def create_records(ids: List, service_metadata: Dict) -> List[Dict]:
    """
    Creates records in the database on the ID list
    """
    params = {"api_key": DOMRIA_TOKEN}
    for param, val in service_metadata["optional"].items():
        params[param] = val

    url = "{base_url}{single_ad}{condition}".format(
        base_url=service_metadata["base_url"],
        single_ad=service_metadata["url_rules"]["single_ad"]["url_prefix"],
        condition=service_metadata["url_rules"]["single_ad"]["condition"]
    )

    realty_models = []
    for realty_id in ids:
        response = requests.get("{url}{id}".format(url=url, id=str(realty_id)),
                                params=params,
                                headers={'User-Agent': 'Mozilla/5.0'})

        try:
            realty_details_data = make_realty_details_data(
                response, service_metadata["model_characteristics"]["realty_details_columns"]
            )
        except json.JSONDecodeError as error:
            print(error)
            raise

        try:
            load_data(RealtyDetailsSchema(), realty_details_data, RealtyDetails)
        except AlreadyInDbException as error:
            print(error)
            continue
            # raise

        try:
            realty_data = make_realty_data(response, service_metadata["model_characteristics"]["realty_columns"])
        except json.JSONDecodeError as error:
            print(error)
            raise

        try:
            realty = load_data(RealtySchema(), realty_data, Realty)
        except AlreadyInDbException as error:
            print(error)
            continue
            # raise
        schema = RealtySchema()
        elem = schema.dump(realty)

        realty_models.append(elem)

    return realty_models


def process_request(search_response: Dict, page: int, page_ads_number: int, metadata: Dict) -> List[Dict]:
    """
    Distributes a list of ids to write to the database and return to the user
    """
    page = page % page_ads_number
    current_items = search_response["items"][
        (page + 1) * page_ads_number - page_ads_number: (page + 1) * page_ads_number
    ]

    return create_records(current_items, metadata)


def open_metadata(path: str) -> Dict:
    """
    Open file with metadata and return content
    """
    try:
        with open(path) as meta_file:
            metadata = json.load(meta_file)
    except json.JSONDecodeError as err:
        print(err)
        raise
    except FileNotFoundError:
        print("Invalid metadata path, or metadata.json file does not exist")
        raise
    return metadata
