# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class Cs410Hw2ScraperItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = Field()
    url = Field()
    #desc = Field()

class PostItem(Item):
    question = Field()
    answers = Field()
    name = Field()
    url = Field()
    time = Field()
    num_ans = Field()
    html = Field()
    tags = Field()