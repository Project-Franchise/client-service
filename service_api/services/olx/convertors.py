"""
Olx convertors
"""

import datetime
import json
import re
import urllib.request
from functools import reduce
from typing import Dict, List
from urllib.error import HTTPError
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from sqlalchemy.orm import make_transient

from service_api import models, session_scope
from ...exceptions import ObjectNotFoundException
from ...utils import recognize_by_alias
from ...utils.selenium import init_driver
from ..interfaces import AbstractOutputConverter


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
        with session_scope() as session:
            realty_type = session.query(models.RealtyType).get(
                self.response["realty_filters"].get("realty_type_id"))

            if realty_type is None:
                raise ObjectNotFoundException(
                    "Realty type not found in OLX handler")

            category_xref = session.query(models.CategoryXRefService).get(
                {"entity_id": realty_type.category_id, "service_id": 2})

        url_main = [category_xref.original_id]
        realty_meta = self.service_metadata["urls"]["search_realty"]["models"]["realty"]
        with session_scope() as session:

            service = session.query(models.Service).filter(
                models.Service.name == self.service_metadata["name"]
            ).first()

            if not service:
                raise Warning(
                    "There is no such service named {}".format(service))

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

        url_details = []
        realty_details_meta = self.service_metadata["urls"]["search_realty"]["models"]["realty_details"]
        for parameter in self.response["characteristics"]:
            for key in self.response["characteristics"][parameter]:
                url_details.append(realty_details_meta[parameter].get(key, None) + "=" +
                                   str(self.response["characteristics"][parameter][key]))
        if url_details:
            url_details[0] = "?" + url_details[0]
            url_details = reduce(lambda x, y: x + "&" + y, url_details)
        url_main = reduce(lambda x, y: x + "/" + y + "/", url_main)
        url = urljoin(urljoin(base_url, url_main), url_details)
        return url


class OlxParser:
    """
    A class for parsing a single OLX ad
    """

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

            realty_data["state_id"] = recognize_by_alias(
                models.State, response.pop("state_id")).id

            cities_by_state = session.query(models.City).filter_by(
                state_id=realty_data["state_id"])
            try:
                realty_data["city_id"] = recognize_by_alias(
                    models.City, response.pop("city_id"), cities_by_state).id
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
            raise Warning(
                "The requested page is no longer available!") from error

        soup = BeautifulSoup(html, "html.parser")
        result = {}

        tags = []
        for tag in soup.find("ul", attrs={"class": self.parser_metadata["tags"]["class"]}):
            if tag.contents:
                tags.append(tag.contents[0].string)

        result.update(self.tag_converter(tags))

        price_string = soup.find(self.parser_metadata["price"]["html_tag"],
                                 attrs={"class": self.parser_metadata["price"]["class"]})

        price = self.price_divider(price_string)

        result["price"] = self.price_converter(price)

        published_at = soup.find(self.parser_metadata["published_at"]["html_tag"],
                                 attrs={"class": self.parser_metadata["published_at"]["class"]})
        result["published_at"] = self.date_converter(published_at.string)

        location = driver.find_element_by_class_name(
            self.parser_metadata["location"]["class"]).text
        result["city_id"], result["state_id"] = self.location_converter(
            location)

        operation_type = soup.findAll(self.parser_metadata["operation_type"]["html_tag"],
                                      attrs={"class": self.parser_metadata["operation_type"]["class"]})
        result["operation_type_id"] = self.operation_type_converter(
            operation_type)

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
        month = re.search("|".join(
            self.parser_metadata["published_at"]["months"].keys()), str(date)).group()
        day = re.search(r"\d{2}", str(date)).group()

        result_date = f"{year}-{self.parser_metadata['published_at']['months'][month]}-{day} 00:00:00"
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

    def get_ads_urls(self, link: str, page_number: int, number_of_ads: int) -> List[str]:
        """
        Function to get all ads urls from OLX according to number of ads
        :param link: link to OLX advertisements with certain filters
        :param page_number: needed to get ads to this page
        :param number_of_ads: returned number of advertisements
        :return: List[str]
        """
        ads, next_page = self.find_all_ads_on_the_page(link)
        gen_num = (page_number + 1) * number_of_ads
        num = gen_num - len(ads)
        while next_page and num > 0:
            more_ads, next_page = self.find_all_ads_on_the_page(next_page)
            num -= len(more_ads)
            if num < 0:
                ads.extend(more_ads[:num])
            else:
                ads.extend(more_ads)
        all_loaded_ads = ads if num >= 0 else ads[:gen_num]
        partial = page_number * number_of_ads
        return all_loaded_ads[partial:]

    def find_all_ads_on_the_page(self, link: str):
        """
        Function to find all ads urls on the page with html.parser
        :param link: link to OLX ads
        :return: all founded advertisement urls plus link to the next page if one exists
        """
        with urllib.request.urlopen(link) as html:
            soup = BeautifulSoup(html, "html.parser")

            if a_tags := soup.find_all("a", {"data-cy": "listing-ad-title"}):
                advertisement_urls = [tag_a['href'] for tag_a in a_tags]
            else:
                advertisement_urls = []

            if next_page := soup.find("a", {"data-cy": "page-link-next"}):
                contains_next_page_link = next_page["href"]
            else:
                contains_next_page_link = None
            return advertisement_urls, contains_next_page_link
