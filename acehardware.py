# Spider: acehardware.com
# Scrapy Version: Scrapy 1.5
# Python Version: Python 3.6.4 :: Pip3

# TEST CLI CRAWLS
# scrapy crawl acehardware.com -a upc=080351812194 -a master_id=00000
# scrapy crawl acehardware.com -a upc=758706362952 -a master_id=00000

from ss.smarter_spiders.spiders.base import BaseSpider, scrapy
from datetime import datetime

class AceSpider(BaseSpider):
    name = "acehardware.com"
    start_path = "https://www.acehardware.com/search/controller.jsp?f={}&kw={}"

    selectors = {
        "product_name": "//*[@id='prodRCol']/div[1]/h2/text()",
        "brand_name": None,
        "manufacturer_name": None,
        "model_num": None,
        "store_sku": None,
        "category": "//div[@id='crumbs']/a/text()",
        "product_type": "//*[@id='prodDescription']/div[2]/div[1]/ul/li[2]/text()",
        "description": "//*[@id='prodDescription']/div[2]/div[1]/ul/*/text()",
        "price": "//*[@id='prodRCol']/div[1]/div[3]/span/text()",
        "weight": None,
        "dimensions": None,
        "height": None,
        "width": None,
        "depth": None,
        "volume": None,
        "color": None,
        "physical_state": None,
        "active_ingredients": None,
        "flash_point": None,
        "ph": None,
        "country_of_origin": None,
        "product_technical_details": None,
        "product_extras": None,
        "product_image_urls": "//*[@id='mainProdImage']/@src",
        "product_sds_url": None
    }

    def start_requests(self):
        # note this will likely break at some point becuase that number will change
        url = self.start_path.format("Taxonomy/ACE/19541496", self.upc)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.response_stats["spider_request_success"] += 1
        self.damage_report["green"] += 1

        product = super(AceSpider, self).parse_item(response)
        super(AceSpider, self).send_to_to_queue(product)
        yield product
