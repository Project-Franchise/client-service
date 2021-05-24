"""
Convertors testing module
"""
import json
import os
from unittest.mock import Mock, MagicMock

import pytest

from service_api.services.domria.convertors import DomRiaOutputConverter, DomRiaInputConverter

path_to_domria_test_data = ["tests", "static_data", "services_test_data", "domria_test_data"]
PATH_TO_OP_CONVERTERS_DATA = os.sep.join([*path_to_domria_test_data, "output_convertors_test_data.json"])
PATH_TO_BUILD_NEW_DICT_DATA = os.sep.join([*path_to_domria_test_data, "ip_build_new_dict_test_data.json"])


def get_converters_data(path: str):
    """
    Return input and expected data to test converters
    """
    with open(path, "r") as file:
        data = json.loads(file.read())
    return data


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


# @pytest.fixture(scope="function")
# def rnd_gen():
#     return random.Random(123456)
#
#
# @pytest.fixture(scope="function")
# def rnd(rnd_gen):
#     return rnd_gen.random()
#
#
# @pytest.fixture()
# def fixture_1(rnd):
#     return rnd
#
#
# @pytest.fixture()
# def fixture_2(rnd):
#     return rnd
#
#
# def test_training(fixture_1, fixture_2):
#     assert fixture_1 == fixture_2
#
#
# def test_training2():
#     assert 2 == 2
