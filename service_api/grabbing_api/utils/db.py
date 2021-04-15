"""
Module with data LoadersFactory and order generator
"""
from collections import defaultdict, deque
from typing import Any, Dict, List, Tuple

from marshmallow.exceptions import ValidationError
from service_api.exceptions import (CycleReferenceException, MetaDataError, ObjectNotFoundException,
                                    ResponseNotOkException)
from service_api.grabbing_api.constants import PATH_TO_CORE_DB_METADATA

from . import core_data_loaders
from .grabbing_utils import open_metadata


class FetchingOrderGenerator:
    """
    Create an sequence ready for fetching that consist of ordered entities based on entites dependencies
    """

    def __init__(self, dependencies: Dict[str, List]) -> None:
        """
        Inithializer of class
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
        Then directed graph is build and BFS is used for finding nedded order of entities.
        """

        adj, roots = defaultdict(list), []

        for name in entities:
            dependencies = sorted(set(entities) & set(self.dependencies[name]))
            if not dependencies:
                roots.append(name)
                continue
            for dependecy in dependencies:
                if dependecy in entities:
                    adj[dependecy].append(name)

        visited = []

        for root in roots:
            self.bfs(adj, root, visited)

        if len(visited) != len(entities):
            raise CycleReferenceException("Cycle dependencies detected during generating entities order")

        return visited

    def bfs(self, adj: Dict, node: str,  visited: List) -> List:
        """
        Bypass the graph using bfs
        :params: Dict: adj (Adjacency structure)
                 str: start node
                 List: list of visited nodes
        """
        queue = deque((node,))

        while queue:
            node = queue.popleft()
            queue.extend((next_node for next_node in adj[node] if next not in visited))
            visited.append(node)

        return visited


class LoadersFactory:
    """
    Load core data to db based on str input
    """

    def __init__(self) -> None:
        """
        Initialization of LoadersFactory thst uses metadata for configuration
        This class can raise MetaDataError
        """
        metadata = open_metadata(PATH_TO_CORE_DB_METADATA)["CORE DATA"]

        for info in metadata.values():
            info["loader"] = getattr(core_data_loaders, info.get("loader", None), None)

        self.__mapper = metadata

    def get_available_entites(self) -> List[str]:
        """
        Returns all possible name of entities that can be loaded
        :return: list[str] with name of entities
        """
        return self.__mapper.keys()

    def divide_input_entities(self, entities: List[str]) -> Tuple[List, List]:
        """
        This function divides given envities on 2 groups (entities that can be loaded, unknown entities)
        :params: List[str]
        :return: tuple[List, List]
        """
        all_entities, input_entities = set(self.__mapper), set(entities)
        return sorted(all_entities & input_entities), sorted(input_entities - all_entities)

    def load(self, **entities_to_load: List) -> Dict[str, Any]:
        """
        Calls mapped loader clasees for keys in params dict input
        :params: dict[str, List] str - name of entity to load (func get_available_entites)
                                 List - args for Loader classes
        :return: dict[str, Any] str - name of entities from input
                                Any - json-like status info about fetching data to db
        """

        can_be_loaded, unknown = self.divide_input_entities(entities_to_load)

        try:
            ordered_entities = FetchingOrderGenerator(
                {key: info["depends_on"] for key, info in self.__mapper.items()}).get_order(can_be_loaded)
        except CycleReferenceException as error:
            print(error.args, error.desc)
            raise MetaDataError(desc=f"Metadata that is used: {PATH_TO_CORE_DB_METADATA}") from error

        statuses = {key: {"status": "Unknown entity"} for key in unknown}
        for entity in ordered_entities:
            try:
                statuses[entity] = {"status": "SUCCESSFUL",
                                    "data": self.__mapper[entity]["loader"]().load(entities_to_load[entity])}
            except ObjectNotFoundException as error:
                error_mesaage = error.args
            except ResponseNotOkException as error:
                error_mesaage = error.args
            except KeyError as error:
                error_mesaage = error.args
            except ValidationError as error:
                error_mesaage = error.messages
            else:
                continue
            statuses[entity] = {"status": "FAILED", "data": error_mesaage}

        return statuses
