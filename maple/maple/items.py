# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MapleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()
    category = scrapy.Field()

