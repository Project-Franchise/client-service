"""
Model convertors
"""
from abc import ABC, abstractmethod
from typing import List, Dict

from service_api.models import State, RealtyType, OperationType, City, Category, Realty, RealtyDetails, Service, \
    StateAlias, RealtyTypeAlias, OperationTypeAlias, CityAlias, CityXRefService, StateXRefService, \
    OperationTypeXRefService, RealtyTypeXRefService


class AbstractModelConvertor(ABC):
    """
    Abstract Model Convertor
    """
    @abstractmethod
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the appropriate models
        """


class ServiceModelConvertor(AbstractModelConvertor):
    """
    Service Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the Service models
        """
        services_data, *_ = args
        return [Service(**service) for service in services_data]


class CategoryModelConvertor(AbstractModelConvertor):
    """
    Category Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the Category models
        """
        categories_data, *_ = args
        return [Category(**category) for category in categories_data]


class RealtyTypeModelConvertor(AbstractModelConvertor):
    """
    RealtyType Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the RealtyType models
        """
        realty_types_data, *_ = args
        return [RealtyType(**realty_type) for realty_type in realty_types_data]


class OperationTypeModelConvertor(AbstractModelConvertor):
    """
    OperationType Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the OperationType models
        """
        operation_types_data, *_ = args
        return [OperationType(**operation_type) for operation_type in operation_types_data]


class StateModelConvertor(AbstractModelConvertor):
    """
    State Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the State models
        """
        states_data, *_ = args
        return [State(**state) for state in states_data]


class CityModelConvertor(AbstractModelConvertor):
    """
    City Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the City models
        """
        cities_data, *_ = args
        return [City(**city) for city in cities_data]


class StateAliasModelConvertor(AbstractModelConvertor):
    """
    StateAlias Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the StateAlias models
        """
        state_alias_data, *_ = args
        return [StateAlias(**state_alias) for state_alias in state_alias_data]


class RealtyTypeAliasModelConvertor(AbstractModelConvertor):
    """
    StateAlias Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the RealtyTypeAlias models
        """
        realty_type_alias_data, *_ = args
        return [RealtyTypeAlias(**realty_type_alias) for realty_type_alias in realty_type_alias_data]


class OperationTypeAliasModelConvertor(AbstractModelConvertor):
    """
    StateAlias Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the OperationTypeAlias models
        """
        operation_type_alias_data, *_ = args
        return [OperationTypeAlias(**operation_type_alias) for operation_type_alias in operation_type_alias_data]


class CityAliasModelConvertor(AbstractModelConvertor):
    """
    StateAlias Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the CityAlias models
        """
        city_alias_data, *_ = args
        return [CityAlias(**city_alias) for city_alias in city_alias_data]


class CityXRefServiceModelConvertor(AbstractModelConvertor):
    """
    StateAlias Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the CityXRefService models
        """
        city_xref_service_data, *_ = args
        return [CityXRefService(**city_xref_service) for city_xref_service in city_xref_service_data]


class StateXRefServiceModelConvertor(AbstractModelConvertor):
    """
    StateAlias Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the StateXRefService models
        """
        state_xref_service_data, *_ = args
        return [StateXRefService(**state_xref_service) for state_xref_service in state_xref_service_data]


class OperationTypeXRefServiceModelConvertor(AbstractModelConvertor):
    """
    StateAlias Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the OperationTypeXRefService models
        """
        op_type_xref_service_data, *_ = args
        return [OperationTypeXRefService(**op_type_xref_service) for op_type_xref_service in op_type_xref_service_data]


class RealtyTypeXRefServiceModelConvertor(AbstractModelConvertor):
    """
    StateAlias Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the RealtyTypeXRefService models
        """
        rt_xref_service_data, *_ = args
        return [RealtyTypeXRefService(**rt_xref_service) for rt_xref_service in rt_xref_service_data]


class RealtyDetailsModelConvertor(AbstractModelConvertor):
    """
    RealtyDetails Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the RealtyDetails models
        """
        realty_details_data, *_ = args
        return [RealtyDetails(**realty_details) for realty_details in realty_details_data]

    @staticmethod
    def convert_to_single_model(realty_det_data):
        """
        Converts deserialized object to the RealtyDetails model
        """
        return RealtyDetails(**realty_det_data)


class RealtyModelConvertor(AbstractModelConvertor):
    """
    Realty Model Convertor
    """
    def convert_to_model(self, *args):
        """
        Converts container of deserialized objects to the Realty models
        """
        realties_data, *_ = args
        return [Realty(**realty) for realty in realties_data]

    @staticmethod
    def convert_to_single_model(realty_data):
        """
        Converts deserialized object to the Realty model
        """
        return Realty(**realty_data)


def get_model_convertors() -> List[AbstractModelConvertor]:
    """
    Function to get all Model convertors
    :return: List[AbstractModelConvertor]
    """
    return [ServiceModelConvertor(), CategoryModelConvertor(), RealtyTypeModelConvertor(),
            OperationTypeModelConvertor(), StateModelConvertor(), CityModelConvertor(),
            RealtyDetailsModelConvertor(), RealtyModelConvertor()]


def get_realty_template(realty_data, realty_details_data) -> Dict:
    """
    :param realty_data: provided info about realty
    :param realty_details_data: provided info about realty details
    :return: realty template according to realty_data, realty_details_data
    """
    realty = RealtyModelConvertor.convert_to_single_model(realty_data)
    realty_details = RealtyDetailsModelConvertor.convert_to_single_model(realty_details_data)
    return {
        "id": realty.id,
        "service": {
            "name": f"TestService{realty.service_id}",
            "id": realty.service_id
        },
        "operation_type": {
            "id": realty.operation_type_id,
            "name": f"TestOperationTypeName{realty.operation_type_id}",
            "self_id": 200 + realty.operation_type_id,
        },
        "realty_type": {
            "name": f"TestRealtyTypeName{realty.realty_type_id}",
            "self_id": 100 + realty.realty_type_id,
            "id": realty.realty_type_id
        },
        "state": {
            "name": f"TestStateName{realty.state_id}",
            "self_id": 110 + realty.state_id,
            "id": realty.state_id
        },
        "city": {
            "self_id": 300 + realty.city_id,
            "name": f"TestCityName{realty.city_id}",
            "id": realty.city_id
        },
        "version": None,
        "realty_details": {
            "published_at": realty_details.published_at,
            "square": realty_details.square,
            "floors_number": realty_details.floors_number,
            "id": realty_details.id,
            "original_url": realty_details.original_url,
            "price": realty_details.price,
            "floor": realty_details.floor,
            "original_id": realty_details.original_id
        },
    }
