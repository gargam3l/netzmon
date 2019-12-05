# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ModemConnectionDetails(scrapy.Item):
    modem_status = scrapy.Field()
    ds_channel_list = scrapy.Field()
    correctable_summary = scrapy.Field()
    us_channel_list = scrapy.Field()
    timestamp = scrapy.Field()

class NetzmonItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
