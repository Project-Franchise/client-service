"""
CLI for app management
"""
import os
import re
from typing import Dict

import click


from service_api import Base, session_scope, flask_app, LOGGER, engine
from service_api.exceptions import MetaDataError
from service_api.utils.db import CoreDataLoadersFactory

BASE_ENTITIES = CoreDataLoadersFactory.get_available_entities()


def parse_entities(ctx, param, values) -> Dict:
    """
    Parse values, split them into entities and params.
    Raises BadOptionUsage if any entity doesn't exist.
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


cli = click.Group(name="commands")


@cli.command("runserver")
@click.option("--port", "-p", show_default=True, type=str, default=os.environ.get("CS_HOST_PORT"), required=True)
@click.option("--host", "-h", show_default=True, type=str, default=os.environ.get("CS_HOST_IP"), required=True)
@click.option("--config", "-c", show_default=True, type=str, default=os.environ.get("FLASK_ENV"), required=True)
def run_app(port, host, config):
    """
    Starts flask application in development mode
    """
    # flask_app.config.from_object(config)
    flask_app.run(port=port, host=host)


@cli.command("run_celery")
def run_celery():
    """
    Start celery application in `beat` mode
    `celery_app` defined in service_api
    `-B` mean beat mode. It's for running periodic tasks
    """
    os.system("celery  -A service_api.celery_app worker -B --loglevel=info")


@cli.command("load_core_data")
@click.option("--column", "-C", "columns", is_flag=False, default=BASE_ENTITIES, show_default=True,
              metavar="<column>", type=click.STRING,
              help="Set entity to load with additional params if possible\n Syntax: -C cities=1,2,3,4",
              multiple=True, callback=parse_entities)
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
    (Params are only available for cities)
    """

    entities = dict.fromkeys(BASE_ENTITIES, []) if load_all else {}
    entities.update(columns)
    factory = CoreDataLoadersFactory()
    try:
        loading_statuses = factory.load(entities)
        LOGGER.debug(loading_statuses)
    except MetaDataError:
        LOGGER.debug("FAILED")


@cli.command("hi")
def printer() -> None:
    """
    Great with you
    """
    LOGGER.debug("Hi")


@cli.command("clearDB")
def clear_db() -> None:
    """
    Clear all tables from DB
    """
    with session_scope() as session:
        for table in Base.metadata.sorted_tables:
            session.query(table).delete()
            LOGGER.debug("%s cleared!", table)
    LOGGER.debug("ALL table cleared")


@cli.command("resetDB")
@click.option("--drop-only", is_flag=True, default=False, help="drops all tables only")
@click.option("--create-only", is_flag=True, default=False, help="create all tables only")
def reset_db(drop_only, create_only) -> None:
    """
    Drops all tables inherited from Base
    and recreates them
    """
    if not(drop_only or create_only):
        # by default input params are false so need to inver them
        drop_only, create_only = True, True

    if input("Are you sure? (y/n)\n").lower() == "y":
        if drop_only:
            LOGGER.info("Dropping db...")
            Base.metadata.drop_all(engine)
            LOGGER.info("Tables droped!")
        if create_only:
            Base.metadata.create_all(engine)
            LOGGER.info("Tables created!")


if __name__ == "__main__":
    cli()
