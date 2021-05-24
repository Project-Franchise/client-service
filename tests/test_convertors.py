"""
Convertors testing module
"""
import json

import pytest

from service_api.services.domria.convertors import DomRiaOutputConverter


def get_convertors_data():
    """
    Return input and expected data to test converters
    """
    with open('tests/static_data/services_test_data/domria_test_data/convertors_test_data.json', "r") as file:
        data = json.loads(file.read())
    return data


class TestDomRiaOutputConverter:
    """
    Class to test DomRiaOutputConverter
    """
    @pytest.mark.parametrize("test_data", get_convertors_data())
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
    ...


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
