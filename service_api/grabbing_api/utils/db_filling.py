from typing import Dict
import json
import sys
import os

sys.path.append(os.getcwd())
from service_api.models import RealtyType, OperationType
from service_api.grabbing_api.resources import session_scope


def fill_db(values: Dict, Model):
    operation_types = []

    for val in values.keys():
        name, id = val, values[val]
        operation_types.append(Model(name=name, original_id=id))

    with session_scope() as session:
        session.add_all(operation_types)
        session.commit()


with open("service_api/static data/main_hardcode.json") as json_file:
    characteristics = json.load(json_file)

    rt_values = characteristics["realty_type"]
    op_values = characteristics["operation_type"]
    fill_db(rt_values, RealtyType)
    fill_db(op_values, OperationType)
