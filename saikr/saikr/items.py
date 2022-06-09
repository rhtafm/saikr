# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SaikrItem(scrapy.Item):
    name = scrapy.Field()
    organizers = scrapy.Field()
    register_time = scrapy.Field()
    contest_time = scrapy.Field()
    types = scrapy.Field()
    url = scrapy.Field()
