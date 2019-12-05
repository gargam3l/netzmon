# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os

from scrapy.exporters import JsonItemExporter
from netzmon.sources import config


def item_type(item):
    # The JSON file names are used (imported) from the scrapy spider.
    return type(item)


class JsonPipeline(object):
    # For simplicity, I'm using the same class def names as found in the,
    # main scrapy spider and as defined in the items.py
    fileNamesJson = ['ModemConnectionDetails']

    def __init__(self):
        os.makedirs("./json", exist_ok=True)
        self.file = open("./json/modem-status-" + str(config.timestamp()) + ".json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class NetzmonPipeline(object):
    def process_item(self, item, spider):
        return item
