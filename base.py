import scrapy
from cssselect.parser import SelectorSyntaxError
import logging
import uuid
from datetime import datetime

from ss.smarter_spiders.services.queue import SmarterSortingQueue
from ss.smarter_spiders.items import ScrapedProduct
from ss.smarter_spiders.normalizers.weight import WeightNormalizer
from ss.smarter_spiders.normalizers.volume import VolumeNormalizer
from ss.smarter_spiders.normalizers.category import CategoryNormalizer
from ss.smarter_spiders.normalizers.base import BaseNormalizer
from ss.smarter_spiders.normalizers.description import DescriptionNormalizer

LOG = logging.getLogger(__name__)

NORMALIZERS = {
    WeightNormalizer.NAME: WeightNormalizer,
    VolumeNormalizer.NAME: VolumeNormalizer,
    CategoryNormalizer.NAME: CategoryNormalizer,
    DescriptionNormalizer.NAME: DescriptionNormalizer,
    "product_extras": DescriptionNormalizer,
    "product_technical_details": DescriptionNormalizer
}


class BaseSpider(scrapy.Spider):
    # name of the spider
    name = None

    # start path for the spider
    start_path = None

    # selector list for getting facets listed in items.py
    selectors = {}

    # Does the spider have custom settings?
    custom_settings = {}

    # What are the types of errors that can occur? {sourceoffailure?_whatfailed?_howdiditfail?}
    response_stats = {
        "website_itemField_NA": 0,
        "spider_itemField_selectorReturnedNone": 0,
        "spider_itemField_selectorFailed": 0,
        "spider_itemField_success": 0,
        "website_request_productSearchNA": 0,
        "spider_request_returnedNone": 0,
        "spider_request_failed": 0,
        "spider_request_success": 0,
        "website_followLink_NA": 0,
        "spider_followLink_returnedNone": 0,
        "spider_followLink_failed": 0,
        "spider_followLink_success": 0
    }
    # How well did the scraper report?
    damage_report = {
        "green": 0,
        "yellow": 0,
        "orange": 0,
        "red": 0
    }

    sds_filetype = "pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "upc" not in kwargs.keys() or "master_id" not in kwargs.keys():
            LOG.error("Missing Keyword, required keywords are upc and master_id")
        else:
            self.upc = kwargs["upc"]
            self.master_id = kwargs["master_id"]
        if self.name is None:
            LOG.error("Missing spider name")
            raise AttributeError

    def parse(self, response):
        super().parse(response)

    def export_data(self, product: ScrapedProduct):
        response = {
            "message_id": str(uuid.uuid4()),
            "published_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "app_id": "ss-scraping",
            "message": {
                "master_id": self.master_id,
                "status_code": 1,
                "response_stats": self.response_stats,
                "damage_report": self.damage_report,
                "bar_code": self.upc,
                "sds_filetype": self.sds_filetype,
                "completed_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "source_url": self.name,
                "facets": dict(product)
            }
        }
        LOG.info("Smarter-Spider Message: %s", response)
        return response

    def follow_link(self, response, next_link):
        # What is the link to follow?
        try:
            LOG.info("Trying to get next page from css")
            next_page = response.css(next_link).extract_first()
            LOG.info("next page: %s", next_page)
        except SelectorSyntaxError:
            LOG.info("Trying to get next page from xpath")
            next_page = response.xpath(next_link).extract_first()
            LOG.info("next page %s", next_page)

        if next_page is not None:
            self.response_stats["spider_followLink_success"] += 1
            self.damage_report["green"] += 1
            return response.follow(next_page, callback=self.parse)
        # What happens if there isn't a link to follow?
        elif next_page is None:
            self.response_stats["spider_followLink_returnedNone"] += 1
            self.damage_report["orange"] += 1
        else:
            self.response_stats["spider_request_returnedNone"] += 1
            self.damage_report["orange"] += 1

    def parse_item(self, response):
        # What are the item fields to select?
        product = ScrapedProduct()
        product["upc"] = self.upc
        product["source_name"] = self.name
        product["source_url"] = response.url
        product["scrape_datetime"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # What happens if a selector fails when gathering data?
        for key, value in self.selectors.items():
            if value is None:
                self.response_stats["website_itemField_NA"] += 1
                self.damage_report["yellow"] += 1
            else:
                try:
                    try:
                        LOG.debug("trying to parse attribute %s, with path %s", key, value)
                        attribute = response.xpath(value).extract()
                    except ValueError:
                        attribute = response.css(value).extract()

                    if attribute:
                        product[key] = self.normalize(key, attribute)
                        self.response_stats["spider_itemField_success"] += 1
                        self.damage_report["green"] += 1
                    else:
                        self.response_stats["spider_itemField_selectorReturnedNone"] += 1
                        self.damage_report["orange"] += 1
                        LOG.warning("Spider selector field for facet %s Returned none", key)

                except Exception as err:
                    self.response_stats["spider_itemField_selectorFailed"] += 1
                    self.damage_report["red"] += 1
                    LOG.error("Failed facet %s with error %s", key, err)
                    raise err
        # export the result
        LOG.info("found product %s", product)
        return product

    @staticmethod
    def normalize(key, value):
        normalizer = NORMALIZERS.get(key, BaseNormalizer)

        return normalizer(value).normalize()

    def send_to_to_queue(self, product):
        parsed_results = self.export_data(product)
        try:
            queue = SmarterSortingQueue()
            queue.publish_scraping_result(parsed_results)
            queue.close_connection()
            LOG.info("sent following to SmarterSortingQueing: %s", parsed_results)
        except KeyError as err:
            LOG.warning("cannot connect to rabbit queue %s, did not send item %s", err, product)
