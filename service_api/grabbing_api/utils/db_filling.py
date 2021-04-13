"""
This module has functions that fill db with realty_type and opertation_type
"""

from typing import Dict

from service_api.grabbing_api.constants import PATH_TO_METADATA
from service_api.grabbing_api.resources import session_scope
from service_api.grabbing_api.utils.grabbing_utils import open_metadata
from service_api.models import OperationType, RealtyType


def fill_db(values: Dict, model):
    """
    Create instance of class model from values
    """
    operation_types = []

    for key, value in values.items():
        operation_types.append(model(name=key, original_id=value))

    with session_scope() as session:
        session.add_all(operation_types)
        session.commit()


characteristics = open_metadata(PATH_TO_METADATA)["DOMRIA API"]["url_characteristics"]

rt_values = characteristics["realty_type"]
op_values = characteristics["operation_type"]
fill_db(rt_values, RealtyType)
fill_db(op_values, OperationType)
