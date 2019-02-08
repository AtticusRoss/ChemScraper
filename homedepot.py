"""
# Spider: Homedepot.com
# Scrapy Version: Scrapy 1.5
# Python Version: Python 3.6.4 :: pip

# TEST CLI CRAWLS
# SDS case
# scrapy crawl homedepot.com -a upc=0320066047772 -a master_id=00000
"""

# import base spider and scrapy
from ss.smarter_spiders.spiders.base import BaseSpider, scrapy
from datetime import datetime


class HomedepotSpider(BaseSpider):
    name = "homedepot.com"
    start_path = "https://www.homedepot.com/s/"
    selectors = {
        "product_name": "//*[@id='productinfo_ctn']/div[2]/div[2]/div[1]/h1/text()",
        "brand_name": "//*[@id='productinfo_ctn']/div[2]/div[2]/div[1]/h2/a/span/text()",
        "manufacturer_name": "//*[@id='productinfo_ctn']/div[2]/div[2]/div[1]/h2/a/span/text()",
        "model_num": "//*[@id='productinfo_ctn']/div[2]/div[1]/div[1]/h2[1]/text()",
        "store_sku": "//*[@id='productinfo_ctn']/div[2]/div[1]/div[1]/h2[3]/span/text()",
        "category": "//*[@id='header-crumb']/li[4]/a/text()",
        "product_type": "//*[@id='specsContainer']/div[5]/div[1]/div[2]/text()",
        "description": "//*[@id='product_description']/div/div[1]/div[3]/div[3]/p[1]/text()",
        "price": "//*[@id='ajaxPrice']/@content",
        "weight": None,
        "dimensions": None,
        "height": "//div[text()='Product Height (in.)']/following::div/text()",
        "width": "//div[text()='Product Width (in.)']/following::div/text()",
        "depth": "//div[text()='Product Depth (in.)']/following::div/text()",
        "volume": "//div[text()='Container Size']/following::div/text()",
        "color": "//div[text()='Color Family']/following::div/text()",
        "physical_state": "//div[text()='Product Form']/following::div/text()",
        "active_ingredients": None,
        "flash_point": None,
        "ph": None,
        "country_of_origin": None,
        "product_technical_details": "//*[@id='specsContainer']/div[5]/text()",
        "product_extras": "//*[@id='specsContainer']/text()",
        "product_image_urls": "//*[@id='mainImage']/@src",
        "product_sds_url": "//*[@id='more-info']/ul/li[3]/a/@href"
    }

    def start_requests(self):
        url = self.start_path + self.upc
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.response_stats["spider_request_success"] += 1
        self.damage_report["green"] += 1
        # Did the request lead to a page on the URL DESTINATION PATH?
        failed_search = response.xpath("//*[@id='productinfo_ctn']/div[2]/div[2]/div[1]/h1/text()").extract_first()
        if failed_search is None:
            self.response_stats["website_request_productSearchNA"] += 1
            self.damage_report["yellow"] += 1
        else:
            product = super(HomedepotSpider, self).parse_item(response)
            super(HomedepotSpider, self).send_to_to_queue(product)
            yield product
