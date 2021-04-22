"""
CLI for interation with service_api
"""

import re
from typing import Dict

import click

from service_api import (Base, flask_app, session_scope)
from service_api.exceptions import MetaDataError

from .grabbing_api.utils.db import LoadersFactory

BASE_ENTITIES = LoadersFactory.get_available_entites()


def parse_entites(ctx, param, values) -> Dict:
    """
    Parse values, split them into entites and params.
    Raises BadOptionUsage if any entity doesn"t exist.
    """

    entities = {}
    for value in values:
        entity, *params = value.split("=")
        params = params or [""]
        if entity not in BASE_ENTITIES:
            raise click.BadOptionUsage("Columns", f"{entity} is not an available entity")
        if len(params) != 1:
            raise click.BadOptionUsage("Columns", f"Params of {entity} is not valid")
        entities[entity] = re.findall(r"\b\d+\b", params[0])

    return entities


@flask_app.cli.command("load_core_data")
@click.option("--column", "-C", "columns", is_flag=False, default=BASE_ENTITIES, show_default=True,
              metavar="<column>", type=click.STRING,
              help="Set entity to load with additional params if possible\n Syntax: -C cities=1,2,3,4",
              multiple=True, callback=parse_entites)
@click.option("--all", "load_all", is_flag=True,
              metavar="BOOL", type=click.BOOL,
              help="Trigger loading of all entities")
def fill_db_with_core_data(columns, load_all) -> None:
    """
    Load data to db based on input params

    Example of usage:\n
        load_core_data -C operation_types -C operation_type_aliases\n
    This will load operation_type_aliases and operation_types to the DB
    If no parameters passed ALL entities from metadata_for_fetching_DB_core.json is loaded.

    Another example of load entities with some parameters:\n
        load_core_data -C cities=1,2,3,4,5\n
    Command above will load cities with next state_ids = [1, 2, 3, 4, 5]
    (Params are only avaliable for cities)
    """

    entities =  dict.fromkeys(BASE_ENTITIES, []) if load_all else  {}
    entities.update(columns)
    factory = LoadersFactory()
    try:
        loading_statuses = factory.load(entities)
        print(loading_statuses)
    except MetaDataError:
        print("FAILED")


@flask_app.cli.command("hi")
def printer() -> None:
    """
    Great with you
    """
    print("Hi")


@flask_app.cli.command("clearDB")
def clear_db() -> None:
    """
    Clear all tables from DB
    """
    with session_scope() as session:
        for table in Base.metadata.sorted_tables:
            session.query(table).delete()
            print(f"{table} cleared!")
    print("ALL table cleared")
