# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CraigsscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    post_id = scrapy.Field()
    post_date = scrapy.Field()
    update_date = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()
    description = scrapy.Field()
    condition = scrapy.Field()
    manufacturer = scrapy.Field()
    model_name = scrapy.Field()
    size = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    keyword = scrapy.Field()
    product_name = scrapy.Field()
