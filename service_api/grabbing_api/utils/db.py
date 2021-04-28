"""
Module with data LoadersFactory and order generator
"""
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from marshmallow.exceptions import ValidationError

from service_api import session_scope
from service_api.exceptions import (CycleReferenceException, MetaDataError, ObjectNotFoundException,
                                    ResponseNotOkException, AlreadyInDbException)
from service_api.grabbing_api.constants import PATH_TO_CORE_DB_METADATA
from service_api.models import RealtyDetails, Realty
from service_api.schemas import RealtyDetailsSchema, RealtySchema
from . import core_data_loaders
from .grabbing_utils import open_metadata, load_data


class FetchingOrderGenerator:
    """
    Create an sequence ready for fetching that consist of ordered entities based on entities dependencies
    """

    def __init__(self, dependencies: Dict[str, List]) -> None:
        """
        Initializer of class
        :params: Dict[str, List] dependencies
            Example:
                {
                    "cities": ["states", "realty_type"],
                    "states": [],
                    "realty_type": ["states"],
                    "operation_type": []
                }
        """
        self.dependencies = dependencies

    def get_order(self, entities: List[str]) -> List[str]:
        """
        Create ordered sequence based on dependencies and entities that need to be ordered

        :params: List[str] entities (should be subset of dependencies.keys() from __init__)
        :return: List[str] list of ordered entities

        At first, Adjacency structure is created from all dependencies and entities.
        During first step collection of all roots (All entities without dependencies) is filled.
        Then directed graph is build and BFS is used for finding needed order of entities.
        """

        adj = defaultdict(list)

        for name in entities:
            dependencies = sorted(set(entities) & set(self.dependencies[name]))
            adj[name].extend(dependencies)

        visited = []

        for entity in adj:
            self.dfs(adj, entity, visited, [])

        return visited

    def dfs(self, adj: Dict, node: str, visited: List, route: List) -> List:
        """
        Bypass the graph using dfs
        :param: adj (Adjacency structure) Dict
        :param: start node str
        :param: list of visited nodes List
        :param: roure List
        """

        if node in route:
            raise CycleReferenceException(
                "Cycle dependencies detected during generating entities order", desc=f"Route: {route}")
        for next_node in adj[node]:
            if next_node not in visited:
                self.dfs(adj, next_node, visited, route)
        if node not in visited:
            visited.append(node)
        return visited


class RealtyLoadersFactory:
    """
    Load realty data to db
    """

    def load(self, all_data: List[Dict]) -> None:
        """
         Calls mapped loader classes for keys in params dict input
        :params: List[Dict] - list of realty
        :return: None - the only loader's responsibility is to load realty and realty details to the database
        """
        for realty, realty_details_id in all_data:
            try:
                load_data(RealtyDetailsSchema(), realty_details_id, RealtyDetails)
            except KeyError as error:
                print(error.args)
            except AlreadyInDbException as error:
                print(error)
                continue

            with session_scope() as session:
                realty_details_id = session.query(RealtyDetails). \
                    filter_by(**realty_details_id).first().id
                realty["realty_details_id"] = realty_details_id
            try:
                load_data(RealtySchema(), realty, Realty)

            except KeyError as error:
                print(error.args)
            except AlreadyInDbException as error:
                print(error)
                continue


class LoadersFactory:
    """
    Load core data to db based on str input
    """
    __METADATA = open_metadata(PATH_TO_CORE_DB_METADATA)["CORE DATA"]

    def __init__(self) -> None:
        """
        Initialization of LoadersFactory that uses metadata for configuration
        This class can raise MetaDataError
        """

        for info in self.__METADATA.values():
            info["loader"] = getattr(core_data_loaders, info.get("loader", None), None)

    @classmethod
    def get_available_entities(cls) -> List[str]:
        """
        Returns all possible name of entities that can be loaded
        :return: list[str] with name of entities
        """
        return list(cls.__METADATA.keys())

    def divide_input_entities(self, entities: List[str]) -> Tuple[List, List]:
        """
        This function divides given entities on 2 groups (entities that can be loaded, unknown entities)
        :params: List[str]
        :return: tuple[List, List]
        """
        all_entities, input_entities = set(self.__METADATA), set(entities)
        return sorted(all_entities & input_entities), sorted(input_entities - all_entities)

    def load(self, entities_to_load: List) -> Dict[str, Any]:
        """
        Calls mapped loader classes for keys in params dict input
        :params: dict[str, List] str - name of entity to load (func get_available_entities)
                                 List - args for Loader classes
        :return: dict[str, Any] str - name of entities from input
                                Any - json-like status info about fetching data to db
        """

        can_be_loaded, unknown = self.divide_input_entities(entities_to_load)

        try:
            ordered_entities = FetchingOrderGenerator(
                {key: info["depends_on"] for key, info in self.__METADATA.items()}).get_order(can_be_loaded)
        except CycleReferenceException as error:
            print(error.args, error.desc)
            raise MetaDataError(desc=f"Metadata that is used: {PATH_TO_CORE_DB_METADATA}") from error

        statuses = {key: {"status": "Unknown entity"} for key in unknown}
        for entity in ordered_entities:
            print(entity)
            try:
                statuses[entity] = {"status": "SUCCESSFUL",
                                    "data": self.__METADATA[entity]["loader"]().load(entities_to_load[entity])}
            except ObjectNotFoundException as error:
                error_message = error.desc or error.args[0]
            except ResponseNotOkException as error:
                error_message = error.desc or error.args[0]
            except KeyError as error:
                error_message = error.args
            except ValidationError as error:
                error_message = error.messages
            else:
                continue
            statuses[entity] = {"status": "FAILED", "data": error_message}

        return statuses
