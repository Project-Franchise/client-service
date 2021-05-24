import json
from typing import Dict, List

import pytest

from service_api import Base, engine
from service_api import LOGGER, session_scope
from service_api.constants import PATH_TO_METADATA
from service_api.exceptions import LoadDataError
from service_api.models import StateAlias, RealtyTypeAlias, OperationTypeAlias, CityAlias
from service_api.services.domria.convertors import DomRiaOutputConverter
from service_api.utils import open_metadata
from tests.convertors import ServiceModelConvertor, OperationTypeModelConvertor, RealtyDetailsModelConvertor, \
    CategoryModelConvertor, StateModelConvertor, RealtyModelConvertor, RealtyTypeModelConvertor, CityModelConvertor, \
    AbstractModelConvertor

PATH_TO_TEST_DATA = r"tests\static_data\services_test_data\domria_test_data\test_db_data.json"


# @pytest.fixture()
def open_testing_data(path: str) -> Dict:
    """
    Open file with testing data and return content
    :param path: path to test data
    :return: dict with test data
    """
    try:
        with open(path, encoding="utf-8") as data_file:
            testing_data = json.load(data_file)
    except json.JSONDecodeError as error:
        LOGGER.error(error)
        raise LoadDataError from error
    except FileNotFoundError as error:
        LOGGER.error("Invalid testing data path, or test_data.json file does not exist")
        raise LoadDataError from error
    return testing_data


# @pytest.fixture()
def fill_db_with_test_data():
    """
    Function for filling testing database
    """
    ready_objects = []
    model_convertors = get_model_convertors()

    testing_data = open_testing_data(PATH_TO_TEST_DATA)
    for convertor, obj_container in zip(model_convertors, testing_data):
        ready_objects.extend(convertor.convert_to_model(testing_data[obj_container]))

    with session_scope() as session:
        session.add_all(ready_objects)
        session.commit()
        ready_objects.clear()


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


# @pytest.fixture()
def get_model_convertors() -> List[AbstractModelConvertor]:
    """
    Function to get all Model convertors
    :return: List[AbstractModelConvertor]
    """
    return [ServiceModelConvertor(), CategoryModelConvertor(), RealtyTypeModelConvertor(),
            OperationTypeModelConvertor(), StateModelConvertor(), CityModelConvertor(),
            RealtyDetailsModelConvertor(), RealtyModelConvertor(), StateAliasModelConvertor(),
            RealtyTypeAliasModelConvertor(), OperationTypeAliasModelConvertor(), CityAliasModelConvertor()]



def setup_function():
    """
    Create all table and instances in DB
    """
    # sql_session.begin()
    Base.metadata.create_all(engine)


def teardown_function():
    """
    Closes sql_session if its open and drop database
    """
    with session_scope() as session:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def get_convertors_data():
    """
    Return input and expected data to test converters
    """
    with open('tests/static_data/services_test_data/domria_test_data/convertors_test_data.json', "r") as f:
        data = json.loads(f.read())
    return data


@pytest.fixture()
def get_metadata():
    """
    Return metadata to test converters
    """
    return open_metadata(PATH_TO_METADATA)["DOMRIA API"]


# class TestDomRiaOutputConverter:
@pytest.mark.parametrize(("expected_realty_data", "expected_realty_details", "response"),
                         [(
        {
            "city_id": 51,
            "operation_type_id": 1,
            "realty_type_id": 1,
            "service_id": 1,
            "state_id": 3
        },
        {
            "floor": 1,
            "floors_number": 2,
            "original_url": "https://dom.ria.com/uk//realty-prodaja-kvartira-dnepr-tsentralnyy-komsomolskaya-ulitsa-19803470.html",
            "price": 25000,
            "published_at": "2021-05-23 12:29:38",
            "square": 25
        },
        {
            "advert_publish_type": 1,
            "advert_type_id": 1,
            "advert_type_name": "\u043f\u0440\u043e\u0434\u0430\u0436\u0430",
            "advert_type_name_uk": "\u043f\u0440\u043e\u0434\u0430\u0436",
            "agency": {
                "agency_id": 31000,
                "agency_type": 1,
                "good_partner": "",
                "logo": "dom/agence/3/310/31000/31000.jpg?v=1603920489862",
                "name": "BALANCE",
                "state_id": 11,
                "user_id": 3356372
            },
            "agency_id": 31000,
            "beautiful_url": "realty-prodaja-kvartira-dnepr-tsentralnyy-komsomolskaya-ulitsa-19803470.html",
            "building_number_str": "64",
            "call_price": 25,
            "characteristics_values": {
                "118": 108,
                "1437": 1434,
                "1650": 1648,
                "209": 1,
                "214": 25,
                "216": 18,
                "218": 5,
                "227": 1,
                "228": 2,
                "234": 25000,
                "242": 239,
                "247": 252,
                "443": 442
            },
            "city_id": 11,
            "city_name": "\u0414\u043d\u0435\u043f\u0440",
            "city_name_uk": "\u0414\u043d\u0456\u043f\u0440\u043e",
            "created_at": "2021-05-23 12:29:32",
            "created_at_ts": 1621762172,
            "currency_type": "$",
            "currency_type_id": 1,
            "date_end": "2021-06-23 12:29:38",
            "date_end_ts": 1624440578,
            "description": "\u041f\u0440\u043e\u0434\u0430\u043c \u0443\u044e\u0442\u043d\u0443\u044e 1 \u043a \u043a\u0432\u0430\u0440\u0442\u0438\u0440\u0443 \u0441 \u0440\u0435\u043c\u043e\u043d\u0442\u043e\u043c \n\u041e\u0442\u0434\u0435\u043b\u044c\u043d\u044b\u0439 \u0432\u0445\u043e\u0434,\u0432\u044b\u0445\u043e\u0434 \u0432 \u043f\u0430\u0440\u043a \u0413\u043b\u043e\u0431\u044b,\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u043f\u0440\u0438\u0441\u0442\u0440\u043e\u0439\u043a\u0438(\u0435\u0441\u0442\u044c \u0437\u0435\u043c\u043b\u044f)",
            "district_id": 15169,
            "district_name": "\u0426\u0435\u043d\u0442\u0440\u0430\u043b\u044c\u043d\u044b\u0439",
            "district_name_uk": "\u0426\u0435\u043d\u0442\u0440\u0430\u043b\u044c\u043d\u0438\u0439",
            "district_type_id": 1,
            "district_type_name": "\u0420\u0430\u0439\u043e\u043d",
            "floor": 1,
            "floors_count": 2,
            "import_id": 106997349636,
            "isBinotel": 1,
            "isNotepad": False,
            "is_calltracking": 1,
            "is_commercial": 1,
            "is_developer": 0,
            "is_exclusive": 0,
            "is_show_building_no": 1,
            "kitchen_square_meters": 5,
            "latitude": 0,
            "living_square_meters": 18,
            "longitude": 0,
            "main_photo": "dom/photo/14640/1464092/146409210/146409210.jpg",
            "metro_station_brunch": 0,
            "metro_station_id": 58,
            "metro_station_name": "\u0412\u043e\u043a\u0437\u0430\u043b\u044c\u043d\u0430\u044f",
            "metro_station_name_uk": "\u0412\u043e\u043a\u0437\u0430\u043b\u044c\u043d\u0430",
            "moderation_date_ts": 1621762181,
            "photos": {
                "146409210": {
                    "file": "dom/photo/14640/1464092/146409210/146409210.jpg",
                    "id": 146409210,
                    "ordering": 5
                },
                "146409211": {
                    "file": "dom/photo/14640/1464092/146409211/146409211.jpg",
                    "id": 146409211,
                    "ordering": 6
                },
                "146409212": {
                    "file": "dom/photo/14640/1464092/146409212/146409212.jpg",
                    "id": 146409212,
                    "ordering": 7
                },
                "146409299": {
                    "file": "dom/photo/14640/1464092/146409299/146409299.jpg",
                    "id": 146409299,
                    "ordering": 8
                }
            },
            "photos_count": 4,
            "price": 25000,
            "priceArr": {
                "1": "25 000",
                "2": "20 455",
                "3": "688 705"
            },
            "price_item": 1000,
            "price_total": 25000,
            "price_type": "\u0437\u0430 \u043e\u0431\u044a\u0435\u043a\u0442",
            "ps_auto_republish": 0,
            "ps_delete_comments": 1,
            "publishing_date": "2021-05-23 12:29:38",
            "publishing_date_ts": 1621762178,
            "quality": 45,
            "realtorVerified": True,
            "realty_id": 19803470,
            "realty_sale_type": 1,
            "realty_type_id": 2,
            "realty_type_name": "\u041a\u0432\u0430\u0440\u0442\u0438\u0440\u0430",
            "realty_type_name_uk": "\u041a\u0432\u0430\u0440\u0442\u0438\u0440\u0430",
            "realty_type_parent_id": 1,
            "realty_type_parent_name": "\u0416\u0438\u043b\u044c\u0435",
            "realty_type_parent_name_uk": "\u0416\u0438\u0442\u043b\u043e",
            "return_on_moderation_date_ts": 1621762320,
            "rooms_count": 1,
            "secondaryUtp": [],
            "state_id": 11,
            "state_name": "\u0414\u043d\u0435\u043f\u0440\u043e\u043f\u0435\u0442\u0440\u043e\u0432\u0441\u043a\u0430\u044f",
            "state_name_uk": "\u0414\u043d\u0456\u043f\u0440\u043e\u043f\u0435\u0442\u0440\u043e\u0432\u0441\u044c\u043a\u0430",
            "street_id": 29964,
            "street_name": "\u0432\u0443\u043b. \u041a\u043e\u043c\u0441\u043e\u043c\u043e\u043b\u044c\u0441\u043a\u0430\u044f \u0443\u043b\u0438\u0446\u0430",
            "street_name_uk": "\u0432\u0443\u043b. \u041a\u043e\u043c\u0441\u043e\u043c\u043e\u043b\u044c\u0441\u044c\u043a\u0430",
            "total_square_meters": 25,
            "updated_at_ts": 1621766068,
            "user": {
                "good_partner_top": "",
                "image": "avatars/all/941/94152/9415210/9415210.jpg?v=1616681963",
                "name": "\u041e\u043b\u044c\u0433\u0430"
            },
            "user_id": 9415210,
            "user_ip": 0,
            "user_package_id": 0,
            "wall_type": "\u043a\u0438\u0440\u043f\u0438\u0447",
            "web_id": ""
        }
    )])
def test_make_realty_details_data(expected_realty_data, expected_realty_details, response):
    """
    Check make_realty_data and make_realty_details methods in DomRiaOutputConverter
    """
    fill_db_with_test_data()
    converter = DomRiaOutputConverter(response, open_metadata(PATH_TO_METADATA)["DOMRIA API"])
    converter.make_realty_details_data()
    converter.make_realty_data()


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
