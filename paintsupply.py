# Spider: paintsupply.com
# Scrapy Version: Scrapy 1.5
# Python Version: Python 3.6.4 :: Pip3

# TEST CLI CRAWLS
# scrapy crawl paintsupply.com -a upc=724504013013 -a master_id=00000
# scrapy crawl paintsupply.com -a upc=070798002715 -a master_id=00000

from ss.smarter_spiders.spiders.base import BaseSpider, scrapy
from datetime import datetime

class PaintsupplySpider(BaseSpider):
    name = "paintsupply.com"
    start_path = "https://www.paintsupply.com/?s={}"

    selectors = {
        "product_name": "//*[@id='product-28697']/div/div[1]/div[2]/div/h1/text()",
        "brand_name": "//span[contains(text(),'Brand Name')]/following::span/text()",
        "manufacturer_name": "//span[contains(text(),'Manufacturer')]/following::span/text()",
        "model_num": "//span[contains(text(),'Model #')]/following::span/text()",
        "store_sku": None,
        "category": "//nav[@class='woocommerce-breadcrumb']//a/text()",
        "product_type": "//*[@id='content']/div/nav/a[2]/text()",
        "description": "//div[@id='description']/p/text()",
        "price": "//*[@id='simple_product_price']/p/span[2]/text()",
        "weight": "//*[@id='tech-specs']/div[2]/ul/li[13]/span[2]/text()",
        "dimensions": None,
        "height": None,
        "width": None,
        "depth": None,
        "volume": "//strong[contains(text(),'Size:')]/following::span/text()",
        "color": None,
        "physical_state": "//strong[contains(text(),'Form:')]/following::span/text()",
        "active_ingredients": "//strong[contains(text(),'Applicable Materials:')]/following::span/text()",
        "flash_point": "//strong[contains(text(),'Flash Point:')]/following::span/text()",
        "ph": "//strong[contains(text(),'pH Range:')]/following::span/text()",
        "country_of_origin": None,
        "product_technical_details": None,
        "product_extras": None,
        "product_image_urls": "//figure[@class='woocommerce-product-gallery__image']/div/a/@href",
        "product_sds_url": "//*[@id='docs']/div/ul/li[1]/a/@href"
    }

    def start_requests(self):
        url = self.start_path.format(self.upc)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.response_stats["spider_request_success"] += 1
        self.damage_report["green"] += 1

        next_page = response.xpath("//a[@rel='bookmark']/@href").extract_first()
        return response.follow(next_page, callback=self.parse_2)

    def parse_2(self, response):
        self.response_stats["spider_request_success"] += 1
        self.damage_report["green"] += 1

        product = super(PaintsupplySpider, self).parse_item(response)
        super(PaintsupplySpider, self).send_to_to_queue(product)
        yield product
