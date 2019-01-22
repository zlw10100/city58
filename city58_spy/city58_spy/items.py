# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class City58SpyItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    update_info = scrapy.Field()
    pay_money = scrapy.Field()
    pay_way = scrapy.Field()
    basic_info = scrapy.Field()
    contact_name = scrapy.Field()
    contact_tel = scrapy.Field()
    config_info = scrapy.Field()
    img_url_list = scrapy.Field()
    district_name = scrapy.Field()
    district_addr = scrapy.Field()
    district_info = scrapy.Field()


class ProxyAddressItem(scrapy.Item):
    """代理地址结构化类"""

    protocol = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
