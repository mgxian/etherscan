# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EtherscanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()


class ContractItem(scrapy.Item):
    address = scrapy.Field()
    name = scrapy.Field()
    balance = scrapy.Field()
    ether_value = scrapy.Field()
    transaction_count = scrapy.Field()
    creator_address = scrapy.Field()
    creator_transaction_hash = scrapy.Field()
    code = scrapy.Field()
    compiler_version = scrapy.Field()
    optimization_enabled = scrapy.Field()
    runs = scrapy.Field()
