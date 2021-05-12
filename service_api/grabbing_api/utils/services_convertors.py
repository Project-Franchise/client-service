"""
Output and input converters for DomRia service
"""
import datetime
import json
from abc import ABC, abstractmethod
import urllib.request
import re
from urllib.error import HTTPError
from urllib.parse import urljoin
from typing import Dict
from functools import reduce
from bs4 import BeautifulSoup

from redis import RedisError
from sqlalchemy.orm import make_transient
from service_api import (CACHE, LOGGER, models, session_scope)
from service_api.errors import BadRequestException
from service_api.exceptions import (BadFiltersException, MetaDataError, ObjectNotFoundException)
from service_api.grabbing_api.constants import (CACHED_CHARACTERISTICS, CACHED_CHARACTERISTICS_EXPIRE_TIME,
                                                PATH_TO_METADATA)
from service_api.grabbing_api.utils import init_driver
from service_api.grabbing_api.utils.limitation import DomriaLimitationSystem
from service_api.grabbing_api.utils.grabbing_utils import (open_metadata, recognize_by_alias)
from service_api.utils import send_request

class AbstractInputConverter(ABC):
    """
    Abstract class for input converters
    """

    def __init__(self, post_body: Dict, service_metadata: Dict, service_name):
        """
        Sets self values and except parsing errors
        """
        self.search_realty_metadata = service_metadata
        self.service_name = service_name
        try:
            self.characteristics = post_body["characteristics"]
            self.realty = post_body["realty_filters"]
            self.additional = post_body["additional"]
        except KeyError as error:
            raise BadRequestException(error.args) from error

    @abstractmethod
    def convert(self):
        """
        Get all items from service by parameters
        :return: str
        :return: Dict
        """


class AbstractOutputConverter(ABC):
    """
    Abstract class for output converters
    """

    def __init__(self, response: Dict, service_metadata: Dict):
        """
        Sets self values
        """
        self.response = response
        self.service_metadata = service_metadata

    @abstractmethod
    def make_realty_data(self) -> Dict:
        """
        Converts a response to a dictionary ready for writing realty in the database
        """

    @abstractmethod
    def make_realty_details_data(self):
        """
        Converts a response to a dictionary ready for writing realty_details in the database
        """


class OLXOutputConverter(AbstractOutputConverter):
    """
    A class for converting characteristics specified by the user into OLX-specified url
    """
    def make_realty_data(self) -> Dict:
        """
        Converts a response to a dictionary ready for writing realty in the database
        """

    def make_realty_details_data(self):
        """
        Converts a response to a dictionary ready for writing realty_details in the database
        """

    def make_url(self) -> str:
        """
        Compose data into OLX-specified url
        """

        base_url = urljoin(
            self.service_metadata["base_url"], self.service_metadata["urls"]["search_realty"]["url_prefix"]) + "/"
        realty_data = {}
        url_main = []
        realty_meta = self.service_metadata["urls"]["search_realty"]["models"]["realty"]
        with session_scope() as session:

            service = session.query(models.Service).filter(
                models.Service.name == self.service_metadata["name"]
            ).first()

            if not service:
                raise Warning("There is no such service named {}".format(service))

            realty_data["service_id"] = service.id
            url_order = self.service_metadata["urls"]["search_realty"]["url_order"]
            for filter_ in url_order:
                if filter_ == "location":
                    for element in realty_meta["location"]:
                        if element in self.response["realty_filters"]:
                            if element == "city_id":
                                entity = session.query(
                                    getattr(models, realty_meta[filter_][element]["model"])).filter_by(
                                    service_id=realty_data["service_id"],
                                    entity_id=self.response["realty_filters"][element]
                                ).first()
                                if entity is not None:
                                    make_transient(entity)
                                    url_main.append(entity.original_id)
                                break
                            entity = session.query(
                                getattr(models, realty_meta[filter_][element]["model"])).filter_by(
                                service_id=realty_data["service_id"],
                                entity_id=self.response["realty_filters"][element]
                            ).first()
                            if entity is not None:
                                make_transient(entity)
                                url_main.append(entity.original_id)
                if filter_ in self.response["realty_filters"]:

                    entity = session.query(getattr(models, realty_meta[filter_]["model"])).filter_by(
                        service_id=realty_data["service_id"], entity_id=self.response["realty_filters"][filter_]
                    ).first()
                    if entity is not None:
                        if filter_ == "operation_type_id":
                            make_transient(entity)
                            entity.original_id = entity.original_id + "-" + \
                                self.service_metadata["sufixes"][url_main[0]]
                        url_main.append(entity.original_id)

        url_details = ["?", ]
        realty_details_meta = self.service_metadata["urls"]["search_realty"]["models"]["realty_details"]
        for parameter in self.response["characteristics"]:
            for key in self.response["characteristics"][parameter]:
                url_details.append(realty_details_meta[parameter].get(key, None) + "=" +
                                   str(self.response["characteristics"][parameter][key]))
        url_details = reduce(lambda x, y: x + "&" + y, url_details)
        url_main = reduce(lambda x, y: x + "/" + y + "/", url_main)
        url = urljoin(urljoin(base_url, url_main), url_details)
        return url


class DomRiaOutputConverter(AbstractOutputConverter):
    """
    A class for converting characteristics specified by the user into data to be sent to DomRia
    """

    def make_realty_details_data(self) -> Dict:
        """
        Composes data for RealtyDetails model
        """

        realty_details_meta = self.service_metadata["urls"]["single_ad"]["models"]["realty_details"]

        values = [self.response.get(val, None) for val in realty_details_meta["fields"].values()]

        realty_details_data = dict(zip(
            realty_details_meta["fields"].keys(), values
        ))

        return realty_details_data

    def make_realty_data(self) -> Dict:
        """
        Composes data for Realty model
        """
        realty_data = {}
        realty_meta = self.service_metadata["urls"]["single_ad"]["models"]["realty"]
        fields = realty_meta["fields"].copy()
        with session_scope() as session:

            service = session.query(models.Service).filter(
                models.Service.name == self.service_metadata["name"]
            ).first()

            if not service:
                raise Warning("There is no such service named {}".format(service))

            realty_data["service_id"] = service.id

            city_characteristics = fields.pop("city_id", None)

            for key, characteristics in fields.items():
                model = characteristics["model"]
                response_key = characteristics["response_key"]

                model = getattr(models, model)

                if not model:
                    raise ObjectNotFoundException("There is no such model named {}".format(model))

                try:
                    obj = recognize_by_alias(model, self.response[response_key])
                except ObjectNotFoundException as error:
                    LOGGER.error("%s, advertisement_id: %s", error.args, self.response.get("realty_id"))
                    raise
                realty_data[key] = obj.id

            if city_characteristics:
                cities_by_state = session.query(models.City).filter_by(state_id=realty_data["state_id"])
                realty_data["city_id"] = recognize_by_alias(models.City,
                                                            self.response[city_characteristics["response_key"]],
                                                            cities_by_state).id

        return realty_data


class DomRiaInputConverter(AbstractInputConverter):
    """
    Class to convert response returned from DomRia to database-ready data
    """

    def convert(self):
        """
        Convert user params to send a request to the server
        """
        params = self.convert_named_field(self.realty)
        params.update(self.convert_characteristic_fields(self.characteristics))
        params["page"] = (self.additional["page"] // self.additional["page_ads_number"]) + 1
        return params

    def convert_characteristic_fields(self, characteristic_filters: Dict):
        """
        Convert domria params (characteristics) to number representation
        """
        with session_scope() as session:
            realty_type_aliases = session.query(models.RealtyType).get(self.realty["realty_type_id"]).aliases

        type_mapper = self.process_characteristics(realty_type_aliases, CACHED_CHARACTERISTICS_EXPIRE_TIME,
                                                   CACHED_CHARACTERISTICS)

        fields, filters = self.search_realty_metadata["models"]["realty_details"]["fields"], {}

        for key, value in characteristic_filters.items():
            service_key = fields[key]["response_key"]
            if service_key in type_mapper:
                filters[type_mapper[service_key]] = {"name": key, "values": value}

        characteristic_filters = self.build_new_dict(filters, self.search_realty_metadata["models"]["realty_details"])

        return characteristic_filters

    def convert_named_field(self, realty_filters: Dict):
        """
        Convert fields names to service names and replace id for its api
        """
        params = {}
        with session_scope() as session:

            realty_meta = self.search_realty_metadata["models"]["realty"]["fields"]

            for param, value in realty_filters.items():
                if param not in realty_meta:
                    continue

                model = realty_meta[param]["model"]
                model = getattr(models, model, None)

                if model is None:
                    raise MetaDataError(message="No model in {param} field of search for realty model")

                service = session.query(models.Service).filter_by(name=self.service_name).first()
                if service is None:
                    raise ObjectNotFoundException("Service with name: {} not found".format(self.service_name))

                xref_record = session.query(model).get({"entity_id": value, "service_id": service.id})

                params[realty_meta[param]["request_key"]] = xref_record.original_id

        return params

    def build_new_dict(self, params: dict, realty_details_metadata) -> dict:
        """
        Method, that forms dictionary with parameters for the request
        """
        new_params, fields_desc = {}, realty_details_metadata["fields"]
        for parameter, value in params.items():
            char_description = fields_desc[value["name"]]
            if char_description["eq"] is not None:
                key = char_description["eq"].format(value=str(parameter))
                new_params[key] = value
                continue
            if (value.get("values")).get("ge"):
                value_from = value.get("values")["ge"]
                key_from = char_description["ge"].format(value_from=str(parameter))
                new_params[key_from] = value_from
            if (value.get("values")).get("le"):
                value_to = value.get("values")["le"]
                key_to = char_description["le"].format(value_to=str(parameter))
                new_params[key_to] = value_to
        new_params["lang_id"] = 4
        return new_params

    def process_characteristics(self, realty_type_aliases, redis_ex_time: Dict, redis_characteristics: str):
        """
        Retrieves data from Redis and converts it to the required format for the request
        """
        cached_characteristics = CACHE.get(redis_characteristics)
        if cached_characteristics is None:
            try:
                characteristics = DomriaCharacteristicLoader().load()
                CACHE.set(redis_characteristics,
                          json.dumps(characteristics),
                          datetime.timedelta(**redis_ex_time))
            except json.JSONDecodeError as error:
                raise json.JSONDecodeError from error
            except RedisError as error:
                raise RedisError(error.args) from error
        else:
            characteristics = json.loads(cached_characteristics)

        for alias in realty_type_aliases:
            if alias.alias in characteristics:
                realty_type_name = alias.alias
                break
        else:
            raise ObjectNotFoundException("Name for realty from aliases type not found")

        try:
            type_mapper = characteristics[realty_type_name]
        except KeyError as error:
            raise BadFiltersException("No such realty type name: {}".format(realty_type_name)) from error

        return type_mapper


class DomriaCharacteristicLoader:
    """
    Loader for domria characteristics
    """

    def __init__(self) -> None:
        try:
            self.metadata = open_metadata(PATH_TO_METADATA)["DOMRIA API"]
        except MetaDataError:
            LOGGER.error("Couldn't load metadata")

    @staticmethod
    def decode_characteristics(dct: Dict) -> Dict:
        """
        Custom object hook.
        Used for finding characteristics
        in "items" dict
        """
        items = {}
        if "items" in dct:
            for fields in dct["items"]:
                if "field_name" in fields:
                    items[fields["field_name"]] = fields["characteristic_id"]
            return items
        return dct

    def load(self, characteristics: Dict = None) -> Dict:
        """
        Function to get characteristics
        and retrieve them in dict
        """

        if characteristics is None:
            characteristics = {}

        chars_metadata, realty_types = self.metadata["urls"]["options"], self.metadata["entities"]["realty_type"]

        params = {"api_key": DomriaLimitationSystem.get_token()}

        for param, val in self.metadata["optional"].items():
            params[param] = val
        params["operation_type"] = 1

        for element in self.metadata["entities"]["realty_type"]:
            url = "{base_url}{condition}{options}".format(
                base_url=self.metadata["base_url"],
                condition=chars_metadata["condition"],
                options=chars_metadata["url_prefix"]
            )

            params[chars_metadata["fields"]["realty_type"]] = realty_types[element]
            req = send_request("GET", url=url, params=params, headers={'User-Agent': 'Mozilla/5.0'})

            requested_characteristics = req.json(object_hook=self.decode_characteristics)
            requested_characteristics = [
                element for element in requested_characteristics if element != {}
            ]

            named_characteristics = {}
            for character in requested_characteristics:
                named_characteristics.update(character)
            characteristics.update({element: named_characteristics})
        return characteristics


class OlxParser:

    """A class for parsing a single OLX ad"""

    def __init__(self, service_metadata):

        self.service_metadata = service_metadata
        self.parser_metadata = service_metadata["urls"]["single_ad"]["parser"]

    def make_data(self, response: dict):
        """
        :param response: a dictionary of all realty data needed in db
        :return: a tuple of two objects: realty and realty_details
        """

        realty_data, realty_details_data = {}, {}

        realty_meta = self.service_metadata["urls"]["single_ad"]["models"]
        fields = realty_meta["realty_details"]["fields"].copy()
        models_list = realty_meta["realty"]["fields"].copy()

        models_list.pop("city_id")
        models_list.pop("state_id")
        models_list.pop("realty_details_id")

        realty_data["service_id"] = 2

        for key in fields.keys():
            realty_details_data[key] = response.pop(key, None)

        with session_scope() as session:

            realty_data["state_id"] = recognize_by_alias(models.State, response.pop("state_id")).id

            cities_by_state = session.query(models.City).filter_by(state_id=realty_data["state_id"])
            try:
                realty_data["city_id"] = recognize_by_alias(models.City, response.pop("city_id"), cities_by_state).id
            except ObjectNotFoundException:
                realty_data["city_id"] = None

            for key in models_list.keys():

                model = models_list[key]["model"]
                model = getattr(models, model)

                if not model:
                    raise Warning(f"There is no such model named {model}")

                try:
                    obj = recognize_by_alias(model, response[key])
                except ObjectNotFoundException as error:
                    print(error.args)
                    break
                realty_data[key] = obj.id

        return realty_data, realty_details_data

    def main_logic(self, link: str):
        """
        :param link: a link to a single OLX page with a realty ad
        :return: calls make_data() in return
        """

        driver = init_driver(link)

        try:
            html = urllib.request.urlopen(link)
        except HTTPError as error:
            raise Warning("The requested page is no longer available!") from error

        soup = BeautifulSoup(html, "html.parser")
        result = {}

        tags = []
        for tag in soup.find("ul", attrs={"class": self.parser_metadata["tags"]["class"]}):
            tags.append(tag.contents[0].string)

        result.update(self.tag_converter(tags))

        price_string = soup.find(self.parser_metadata["price"]["html_tag"],
                                 attrs={"class": self.parser_metadata["price"]["class"]})

        price = self.price_divider(price_string)

        result["price"] = self.price_converter(price)

        published_at = soup.find(self.parser_metadata["published_at"]["html_tag"],
                                 attrs={"class": self.parser_metadata["published_at"]["class"]})
        result["published_at"] = self.date_converter(published_at.string)

        location = driver.find_element_by_class_name(self.parser_metadata["location"]["class"]).text
        result["city_id"], result["state_id"] = self.location_converter(location)

        operation_type = soup.findAll(self.parser_metadata["operation_type"]["html_tag"],
                                      attrs={"class": self.parser_metadata["operation_type"]["class"]})
        result["operation_type_id"] = self.operation_type_converter(operation_type)

        result["original_url"] = self.url_converter(link)

        original_id = soup.find(self.parser_metadata["original_id"]["html_tag"],
                                attrs={"class": self.parser_metadata["original_id"]["class"]})
        result["original_id"] = int(original_id.text[4:])

        return self.make_data(result)

    def price_divider(self, data):
        """
        :param data: an HTML row which contains the price and the currency sign ($, € or грн.)
        :return: divided float price and a currency sign as str
        """
        data = str(data)

        price = re.search(">(.*?)<!--", data)
        price = price.group(1).replace(" ", "")

        currency = re.search("<!-- -->(.*?)</h3>", data)
        currency = str(currency.group(1))[9:]

        return float(price), currency

    def price_converter(self, price):
        """
        :param price: the price fetched from the parser
        :param currency: the currency needed to be converted to USD (for example $, € or грн.)
        :return: float price converted to usd
        """
        if price[1] == "$":
            return price[0]

        with urllib.request.urlopen("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?&json") as url:

            data = json.loads(url.read().decode())
            usd = next(x for x in data if x["cc"] == "USD")
            usd_currency = round(usd["rate"], 2)

            usd_price = None

            if price[1] == "грн.":
                usd_price = price[0] / usd_currency

            elif price[1] == "€":
                eur = next(x for x in data if x["cc"] == "EUR")
                eur_currency = round(eur["rate"], 2)

                usd_price = price[0] * eur_currency / usd_currency

            if not usd_price:
                raise Warning("Wrong currency entered!")

        return round(usd_price, 2)

    def date_converter(self, date: str):
        """
        :param date: string in the following format(example): 05 травня 2021 р. or Сьогодні о 19:48
        :return: date formatted as yyyy-mm-dd hh-mm-ss
                    (as for the above examples: 2021-05-05 00:00:00 or 2021-05-11 19:48:00
        """
        if date.startswith("Сьогодні"):
            day = datetime.date.today()
            time = re.search(r"\d\d:\d\d", date).group()

            result = day.strftime("%Y-%m-%d") + f" {time}:00"
            return result

        year = re.search(r"\d{4}", str(date)).group()
        month = re.search("|".join(self.parser_metadata["published_at"]["months"].keys()), str(date)).group()
        day = re.search(r"\d{2}", str(date)).group()

        result_date = f"{year}-{day}-{self.parser_metadata['published_at']['months'][month]} 00:00:00"
        return result_date

    def tag_converter(self, tags):
        """
        :param tags: list of tags from OLX
        :return: dictionary with floor, floors_number, realty_type
        """
        result = {}
        realty_details_fetched = False

        for tag in tags:
            tag = str(tag)

            if tag.startswith(self.parser_metadata["tags"]["floor"]):
                position = tag.find(":")
                result["floor"] = int(tag[position + 2:])

            elif tag.startswith(self.parser_metadata["tags"]["floors_number"]):
                position = tag.find(":")
                result["floors_number"] = int(tag[position + 2:])

            elif tag.startswith(self.parser_metadata["tags"]["square"]):
                square = re.search(": (.*?) м", tag).group(1)
                result["square"] = float(square)

            elif re.search("|".join(self.parser_metadata["tags"]["realty_type"]), tag) and not realty_details_fetched:
                position = tag.find(":")

                if tag.startswith(self.parser_metadata["tags"]["realty_type"][0]):
                    result["realty_type_id"] = tag[position + 2:]
                    realty_details_fetched = True
                result["realty_type_id"] = tag[position + 2:]

        return result

    def location_converter(self, location: str):
        """
        :param location: a string, which contains a city and a state
        (example:
        Вінниця, Ленінський
        Вінницька область
        :return: a tuple with two elements: city, state (example: Вінниця, Вінницька)
        """
        city_with_district = location[:location.find("\n") - 1]
        city = city_with_district.split(",")

        state = re.search("(.*?) область", location)

        return city[0], state.group(1)

    def operation_type_converter(self, operation_type: list):
        """
        :param operation_type: a list of links, which may contain operation type
        :return: a string with a matching operation type
        """
        for element in [operation_type[2], operation_type[3]]:
            if res_operation_type := re.search("|".join(self.parser_metadata["operation_type"]["types"]), str(element)):
                return res_operation_type.group()

        return None

    def url_converter(self, link: str):
        """
        :param link: a link to single OLX ad
        :return: a unique part or url
        """
        link = link[len(self.parser_metadata["link"]):]
        result_url = re.search(".*?html", link)

        return result_url.group()
