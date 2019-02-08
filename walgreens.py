# Spider: walgreens.com
# Scrapy Version: Scrapy 1.5
# Python Version: Python 3.6.4 :: Pip3

# TEST CLI CRAWLS
# scrapy crawl walgreens.com -a upc=38151900471 -a master_id=00000

from ss.smarter_spiders.spiders.base import BaseSpider, scrapy
from datetime import datetime

class WalgreensSpider(BaseSpider):
    name = "walgreens.com"

    start_path = "https://www.walgreens.com/search/results.jsp?Ntt={}"

    selectors = {
        "product_name": "//span[@id='productTitle']/text()",
        "brand_name": None,
        "manufacturer_name": "(//div[@name='description-Details']//text())[last()]",
        "model_num": None,
        "store_sku": "(//p[contains(@class, 'universal-product-code')]/text())[last()]",
        "category": None,
        "product_type": None,
        "description": "//div[@itemprop='description']/ul//span/text()",
        "price": None,
        "weight": "(//p[contains(@class, 'universal-Shipping-Weight')]/text())[last()]",
        "dimensions": "(//p[contains(@class, 'universal-product-inches')]/text())[last()]",
        "height": None,
        "width": None,
        "depth": None,
        "volume": "//span[@id='productSizeCount']/text()",
        "color": None,
        "physical_state": None,
        "active_ingredients": "//div[@name='description-Ingredients']//span/text()",
        "flash_point": None,
        "ph": None,
        "country_of_origin": "//p[starts-with(text(), 'Made in')]/text()",
        "product_technical_details": "//table[contains(@class, 'pi-table wag')]//td/text()",
        "product_extras": "//div[@name='description-Warnings']//p/text()",
        "product_image_urls": None,
        "product_sds_url": None,
    }

    def start_requests(self):
        url = self.start_path.format(self.upc)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.response_stats["spider_request_success"] += 1
        self.damage_report["green"] += 1

        product_name = response.xpath(self.selectors["product_name"]).extract_first()

        if product_name:

            product = super(WalgreensSpider, self).parse_item(response)
            product["price"] = self.get_price(response)

            super(WalgreensSpider, self).send_to_to_queue(product)
            yield product
        else:
            # Find a link to follow?
            yield super(WalgreensSpider, self).follow_link(
                response,
                "//div[@class='prod-thumbnail wag-thumbnail']/a/@href")

    def get_price(self, response):
        dollars = response.xpath("//span[@id='regular-price']/span/text()").extract_first()
        cents = response.xpath("//span[@id='regular-price']/span/following::sup/text()").extract_first()
        if dollars and cents:
            return "{}.{}".format(dollars, cents)

        return response.xpath("//span[@id='sales-price-info']/text()").extract_first()
