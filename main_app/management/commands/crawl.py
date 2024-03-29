from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from scrapy_app.scrapy_app import settings as my_settings
from scrapy_app.scrapy_app.spiders import RecipeFetcher


class Command(BaseCommand):
    help = "Release the spiders"

    def add_arguments(self, parser):
        parser.add_argument("--includes", type=str)
        parser.add_argument("--excludes", type=str)
        # super().add_arguments(parser)

    def handle(self, *args, **options):
        sett = Settings()
        sett.setmodule(my_settings)

        process = CrawlerProcess(settings=sett)
        process.crawl(RecipeFetcher.RecipeSpider, ingredients=options["includes"], excludes=options["excludes"],
                      LOG_ENABLED=False)
        process.start()
