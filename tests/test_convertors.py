"""
Convertors testing module
"""
import json
import os
from unittest.mock import Mock, MagicMock, patch

import pytest

from service_api import LOGGER
from service_api.exceptions import LoadDataError
from service_api.services.domria.convertors import DomRiaOutputConverter, DomRiaInputConverter

path_to_domria_test_data = ["tests", "static_data", "services_test_data", "domria_test_data"]
PATH_TO_OP_CONVERTERS_DATA = os.sep.join([*path_to_domria_test_data, "output_convertors_test_data.json"])
PATH_TO_BUILD_NEW_DICT_DATA = os.sep.join([*path_to_domria_test_data, "ip_build_new_dict_test_data.json"])
PATH_TO_CONVERT_FIELD_DATA = os.sep.join([*path_to_domria_test_data, "ip_convert_char_fields_test_data.json"])
PATH_TO_CONVERT_FIELD_METADATA = os.sep.join([*path_to_domria_test_data, "metadata_ip_convert_char_fields.json"])
PATH_TO_CACHED_CHARACTERISTICS = os.sep.join([*path_to_domria_test_data, "cached_characteristics.json"])


def get_converters_data(path: str):
    """
    Return input and expected data to test converters
    """
    try:
        with open(path, encoding="utf-8") as data_file:
            testing_data = json.load(data_file)
    except FileNotFoundError as error:
        LOGGER.error("Invalid testing data path, or test_data.json file does not exist")
        raise LoadDataError from error
    except json.JSONDecodeError as error:
        LOGGER.error(error)
        raise LoadDataError from error
    return testing_data


class TestDomRiaOutputConverter:
    """
    Class to test DomRiaOutputConverter
    """

    @pytest.mark.parametrize("test_data", get_converters_data(PATH_TO_OP_CONVERTERS_DATA))
    def test_make_realty_data(self, test_data, get_metadata, database):
        """
        Check make_realty_data and make_realty_details methods in DomRiaOutputConverter
        """
        converter = DomRiaOutputConverter(test_data["response"], get_metadata)

        assert converter.make_realty_details_data() == test_data["expected_realty_details"]
        assert converter.make_realty_data() == test_data["expected_realty_data"]


class TestDomRiaInputConverter:
    """
    Class to test DomRiaInputConverter
    """

    @pytest.mark.parametrize("test_data", get_converters_data(PATH_TO_BUILD_NEW_DICT_DATA))
    def test_build_new_dict(self, test_data):
        """
        Check if build new dict return needed data
        """
        service_metadata, service_name = Mock(), Mock()

        mock_body = MagicMock()
        post_body = {"characteristics": {}, "realty_filters": {}, "additional": {}}
        mock_body.__getitem__.side_effect = post_body.__getitem__

        converter = DomRiaInputConverter(mock_body, service_metadata, service_name)
        new_params = converter.build_new_dict(test_data["params"], test_data["realty_details_metadata"])

        assert test_data["new_params"] == new_params

    @pytest.mark.parametrize("test_data", get_converters_data(PATH_TO_CONVERT_FIELD_DATA))
    def test_convert_characteristic_fields(self, test_data, database, open_testing_data):
        """
        Check converting limited user data to DomRia search characteristics
        """
        service_name = Mock()
        service_metadata = open_testing_data(PATH_TO_CONVERT_FIELD_METADATA)

        mock_body = MagicMock()
        post_body = {"characteristics": {}, "realty_filters": {"realty_type_id": 1}, "additional": {}}
        mock_body.__getitem__.side_effect = post_body.__getitem__

        converter = DomRiaInputConverter(mock_body, service_metadata, service_name)
        with patch("service_api.CACHE") as mock_cache:
            mock_cache.get.side_effect = open_testing_data(PATH_TO_CACHED_CHARACTERISTICS)
            new_filters = converter.convert_characteristic_fields(test_data["input_char_filters"])

            assert test_data["output_char_filters"] == new_filters
