# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem


# class ScrapyAppItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

class RecipeItem(scrapy.Item):

    title = scrapy.Field()
    details = scrapy.Field()
    ingredients = scrapy.Field()
    directions = scrapy.Field()
    nutrients = scrapy.Field()
    cooking_info = scrapy.Field()
    link = scrapy.Field()
    pass


