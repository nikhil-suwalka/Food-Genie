from django.core.management.base import BaseCommand
from scrapy_app.scrapy_app.spiders import RecipeFetcher
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
from scrapy_app.scrapy_app import settings as my_settings

class Command(BaseCommand):
    help = "Release the spiders"

    def add_arguments(self, parser):
        parser.add_argument("arg", type=str)
        # super().add_arguments(parser)

    def handle(self, *args, **options):
        print("asdfghjkl")
        print(options["arg"])
        sett = Settings()
        sett.setmodule(my_settings)

        process = CrawlerProcess(settings=sett)
        # process = CrawlerRunner(settings=sett)

        # process = CrawlerProcess(get_project_settings())
        process.crawl(RecipeFetcher.RecipeSpider, ingredients=options["arg"])
        process.start()
        # process.join()


