import os
import sys
from typing import List, Dict

import requests
from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta
from sqlalchemy.orm import Session

sys.path.append(os.getcwd())
from service_api import session


def load_data(data: Dict, session: Session, ModelSchema: SchemaMeta) -> SchemaMeta:
    try:
        res_data = ModelSchema().load(data)
    except ValidationError as error:
        print(error.messages)
        print("Validation failed", 400)
        return ModelSchema().load(dict())

    session.add(res_data)
    session.commit()
    return res_data


def make_realty_details_data(response: requests.models.Response, realty_details_keys: Dict) -> Dict:
    original_keys = [response.json()[val] for val in realty_details_keys.values()]
    self_keys = realty_details_keys.keys()

    realty_details_data = {
        key: value for (key, value) in
        zip(self_keys, original_keys)
    }

    return realty_details_data


def make_realty_data(response: requests.models.Response, realty_keys: List) -> Dict:
    realty_data = dict()
    for keys in realty_keys:
        id, model, response_key = keys
        realty_data[id] = (session.query(model).filter(
            model.original_id == response.json()[response_key]
        ).first()).id

    return realty_data
