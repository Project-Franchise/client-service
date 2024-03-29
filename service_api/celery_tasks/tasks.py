"""
Celery tasks. Loading realties to db logic.
"""
from typing import Dict

from celery import group
from sqlalchemy import select

from service_api import LOGGER, session_scope
from ..constants import PAGE_LIMIT
from ..errors import BadRequestException
from ..exceptions import BadFiltersException, LimitBoundError
from ..models import (AdditionalFilters, OperationType, Realty, RealtyDetails, RealtyType, State)
from ..schemas import (AdditionalFilterParametersSchema, RealtyDetailsInputSchema, RealtySchema, filters_validation)
from ..utils.db import RealtyFetcher
from . import celery_app
from .updaters import RealtyUpdater


@celery_app.task
def load_realties_by_filters(filters: Dict):
    """
    Calls RealtyFetcher to load realties by input filters.

    :param filters: Dict - dict of filters
    :returns: None
    """

    page = 1
    while page < PAGE_LIMIT:
        filters["page"] = page
        filters["page_ads_number"] = 100
        try:
            realty_dict, realty_details_dict, additional_params_dict, *_ = filters_validation(
                filters,
                [(Realty, RealtySchema),
                 (RealtyDetails, RealtyDetailsInputSchema),
                 (AdditionalFilters, AdditionalFilterParametersSchema)])
        except BadFiltersException as error:
            raise BadRequestException from error

        request_filters = {
            "realty_filters": realty_dict,
            "characteristics": realty_details_dict,
            "additional": additional_params_dict
        }

        if not RealtyFetcher(request_filters).fetch(limit_data=True):
            break
        page += 1


@celery_app.task
def fill_db_with_realties():
    """
    Create all minimally needed filter combinations.
    Trigger realties loading and process them in parallel.
    """
    with session_scope() as session:
        query = select((RealtyType.id, State.id, OperationType.id))
        filters = session.execute(query).all()
    filters = [{"realty_type_id": realty_type_id,
                "state_id": state_id,
                "operation_type_id": operation_type_id}
               for realty_type_id, state_id, operation_type_id in filters]

    group_of_tasks = group([load_realties_by_filters.s(f) for f in filters])
    group_of_tasks()


@celery_app.task()
def update_realties():
    """
    Passes on all records of realty and realty details in a DB,
    compares with the information on service and updates if necessary
    """
    try:
        updater = RealtyUpdater()
    except LimitBoundError as error:
        LOGGER.error(error.args[0])
    else:
        updater.update_records()
