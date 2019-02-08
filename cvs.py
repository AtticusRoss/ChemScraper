import logging
import json
from scrapy import Request
from ss.smarter_spiders.normalizers.weight import WeightNormalizer
import re

from ss.smarter_spiders.spiders.base import BaseSpider

LOG = logging.getLogger(__name__)


class CVSSpider(BaseSpider):
    name = "cvs.com"

    single_item_start_path = "https://www.cvs.com/search/?cp=%5B%7B%22key%22%3A%22source%22%2C%22value%22%3A%22trending%22%7D%5D&searchTerm={}"
    single_item_path_selectors = ["redirect"]
    fullsite_start_path = "https://www.cvs.com/shop"
    fullsite_path_selectors = [
        "//div[@id='promo-category-grid']",
        "//div[@class='col-xs-6 col-md-3']/a/@href",
        "//div[@class='product-tile-set']//a/@href"
    ]
    selectors = {
        "product_name": '//*[@*="main-title"]/text()',
        "brand_name": None,
        "manufacturer_name": None,
        "model_num": '//*[@*="product-info-typography__details-meta"]/text()',
        "store_sku": None,
        "category": '//*[@class="cvsui-c-breadcrumb__list"]/text()',
        "product_type": None,
        "description": '//*[@id="tabContentContainer"]/cvs-content/text()',
        "price": "//*[@id='top-heading']/div[2]/div[1]/div[3]/text()",
        "weight": '//*[@*="product-info-typography__details-meta"]/text()',
        "dimensions": None,
        "height": None,
        "width": None,
        "depth": None,
        "volume": '//*[@*="product-info-typography__details-meta"]/text()',
        "color": None,
        "physical_state": None,
        "active_ingredients": '//*[@*="selectedSku.p_Product_Ingredients"]/text()',
        "ph": None,
        "country_of_origin": None,
        "product_technical_details": None,
        "product_extras": None,
        "product_image_url": '//*[@class="slides"][1]/a/@href',
        "product_sds_url": None,
        "shipping_info": None,
        "nutrition": '//table[@class="nutritional-facts"]/li/text()',
        "product_extras": "//cvs-content[@contentpath='selectedSku.p_Product_Warnings']/text()",

        }

    splash=True

    def parse_weight(response):
        text=response.xpath('//*[@*="product-info-typography__details-meta"]/text()')
        
        sku_pattern = re.compile("(Item# \d{0,7})")
        weight_pattern = re.compile("(\d{0,10}\.\d{0,7} lbs.)")

        weight_result = weight_pattern.match(response)
        sku_result = sku_pattern.match(response)
        
        refined_sku_pattern = re.compile("\d{1,15}")
        refined_weight_pattern = re.compile("(\d{0,10}\.\d{0,7} )")
        
        sku = refined_sku_pattern.match(sku_result)
        weight = WeightNormalizer(refined_weight_pattern.match(weight_result))
        return(weight, sku)