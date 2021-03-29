from typing import Dict

from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta
from sqlalchemy.orm import Session


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
