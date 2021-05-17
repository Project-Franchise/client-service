"""
Olx handler module
"""
from ..interfaces import AbstractServiceHandler
from .convertors import OLXOutputConverter, OlxParser


class OlxServiceHandler(AbstractServiceHandler):
    """
    Handler class for OLX service
    """

    def get_latest_data(self):
        """
        Method that realise the logic of sending request to OLX and getting items
        :return: List[Dict]
        """
        url = OLXOutputConverter(self.post_body, self.metadata).make_url()
        olx_parser = OlxParser(self.metadata)
        parsed_links = olx_parser.get_ads_urls(url, self.post_body["additional"]["page"],
                                               self.post_body["additional"]["page_ads_number"])
        records = []
        for link in parsed_links:
            records.append(olx_parser.main_logic(link))
        return records
