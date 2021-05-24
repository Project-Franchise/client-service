"""
Interfaces for loaders
"""

import csv
from abc import ABC, abstractmethod

from ..constants import PATH_TO_METADATA, PATH_TO_PARSER_METADATA
from ..utils import load_data, open_metadata


class BaseLoader(ABC):
    """
    Abstract class for loading static base date to DB (exp. cities, states, realty_types...)
    """

    def __init__(self) -> None:
        """
        Fetches info from metadata
        Raise MetaDataError
        """
        self.metadata = open_metadata(PATH_TO_METADATA) | open_metadata(PATH_TO_PARSER_METADATA)

    @abstractmethod
    def load(self, *args, **kwargs) -> None:
        """
        Main function of retrieving and loading data to db
        """
        return None


class XRefBaseLoader(BaseLoader):
    """
    Base Loader for cross reference tables
    """

    def __init__(self) -> None:
        """
        Loads domria metadata
        """
        super().__init__()
        self.domria_meta = self.metadata["DOMRIA API"]


class CSVLoader(BaseLoader):
    """
    Aliases loader from csv file
    Class attributes that must be initialized:
        model: Alias model
        model_schema: Alias schema
        path_to_file: str
    """

    @property
    @abstractmethod
    def model(self):
        """
        Alias model
        """
        ...

    @property
    @abstractmethod
    def model_schema(self):
        """
        Alias schema for model
        """
        ...

    @property
    @abstractmethod
    def path_to_file(self):
        """
        Path to aliases csv file
        """
        ...

    def __init__(self) -> None:
        """
        Open and load info from csv file
        """
        with open(self.path_to_file, encoding="utf-8", mode="r") as file:
            self.data = list(csv.DictReader(file))

    def load(self, *args, **kwargs) -> None:
        """
        Load models from csv file located in path_to_file
        """
        for row in self.data:
            load_data(self.model_schema(), row, self.model)
