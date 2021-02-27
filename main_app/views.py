import time
from urllib.request import urlopen

import scrapy
from django.http import HttpResponse
from django.shortcuts import render
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from crochet import setup
from scrapy.utils.log import configure_logging
from scrapy_app.scrapy_app import settings as my_settings

# from .models import Ingredient, Recipe
from django.shortcuts import render, redirect
from scrapy_app.scrapy_app.spiders import RecipeFetcher


# Create your views here.
# process = CrawlerProcess(get_project_settings())
#
# process.crawl(RecipeFetcher.RecipeSpider)
# process.join()

def crawl():
    # html_resp = urlopen("https://www.allrecipes.com/search/results/?ingIncl=paneer,potato&sort=re")
    response = scrapy.http.HtmlResponse("https://www.allrecipes.com/search/results/?ingIncl=paneer,potato&sort=re")
    title = response.xpath("//div").extract()
    return title


def homeview(request):
    # ing = Ingredient(name="Paneer").save()
    # rec = Recipe(name="First", details="details", ingredients=["1", "2"], calories=300.5, directions=["d1"],
    #        nutrients="{}", preparation_time="11", cooking_time="22", total_time="33").save()
    # rec.ingredient.connect(ing)
    #
    # process = CrawlerRunner(get_project_settings())
    #
    # process.crawl(RecipeFetcher.RecipeSpider)
    # process.join()


    crawler_settings = Settings()
    setup()
    # configure_logging()
    crawler_settings.setmodule(my_settings)
    runner = CrawlerRunner(settings=crawler_settings)
    d = runner.crawl(RecipeFetcher.RecipeSpider)
    runner.join()
    print(d)
    # time.sleep(8)

    return HttpResponse()
