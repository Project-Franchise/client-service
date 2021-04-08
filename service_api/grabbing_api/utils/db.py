from abc import ABC, abstractmethod

class BaseLoader(ABC):
    """
    Abstract class for loading static base date to DB (exmp. cities, states, realty_types...)
    """

    @abstractmethod
    @property
    def name(self):
        """
        Name of this class
        Is used in metadata
        """
        pass

    @abstractmethod
    def load_to_db(self) -> None:
        """
        Main function of retrieving and loading data to db
        """
        pass


