import scrapy
import logging
from ..items import RecipeItem


class RecipeSpider(scrapy.Spider):
    name = "RecipeFetcher"
    allowed_domains = ['www.allrecipes.com']

    def __init__(self, ingredients=None, **kwargs):
        ingredients = ingredients.replace("_", " ")

        ingredients = ingredients.split(",")


        # rec = ["paneer", "potato"]

        link = "https://www.allrecipes.com/search/results/?"
        for i in range(len(ingredients)):
            link += "&IngIncl="
            link += ingredients[i]


        # self.start_urls = [link[:-1]+"&sort=re"]
        self.start_urls = [link]

        super().__init__(**kwargs)

    def parse(self, response, **kwargs):

        # NEW
        title = response.xpath("//div/div/div/a/h3[@class='card__title']/text()").getall()
        links = response.xpath("//div[@class='component card card__recipe card__facetedSearchResult']/div/div/a/@href").getall()
        details = response.xpath("//div[@class='component card card__recipe card__facetedSearchResult']/div/div/div[@class='card__summary']/text()").getall()

        # title = response.xpath("//h3/a/span/text()").getall()
        # links = response.xpath("//h3/a/@href").getall()
        # details = response.xpath("//a/div[@class='fixed-recipe-card__description']/text()").getall()

        for i in range(len(links)):
            # yield {
            #     "title": title[i],
            #     "details": details[i],
            #     "link": links[i],
            # }

            yield scrapy.Request(url=links[i], callback=self.parse_links,
                                 meta={"title": title[i].strip(), "details": details[i].strip(), "link": links[i]})

    def parse_links(self, response):
        logging.info(response.url)

        ingredients = response.xpath("//label/span/span[@class='ingredients-item-name']/text()").getall()
        ingredients = [x.strip() for x in ingredients]
        directions = response.xpath("//li/div/div/p/text()").getall()
        directions = [x for x in directions]

        nutrition_dict = {}

        nutrition_dict["total calories"] = response.xpath(
            "//div[@class='nutrition-top light-underline']/span/following-sibling::text()").get().strip()

        nutritions = response.xpath("//div[@class='nutrition-body']/div")

        for nutrition in nutritions:
            nutrition_dict[nutrition.xpath("span[1]/text()").get().strip()] = nutrition.xpath(
                "span[1]/span[2]/text()").get().strip()

        cooking_details = {}
        cookings = response.xpath("//section[@class='recipe-meta-container two-subcol-content clearfix']/div[1]/div")
        for cooking in cookings:
            cooking_details[cooking.xpath("div[1]/text()").get().strip().split(':')[0]] = cooking.xpath(
                "div[2]/text()").get().strip()

        recipe = RecipeItem()

        for item in ["prep", "cook", "total"]:
            if item not in cooking_details:
                cooking_details[item] = "N/A"

        recipe["title"] = response.request.meta["title"]
        recipe["details"] = response.request.meta["details"]
        recipe["ingredients"] = ingredients
        recipe["directions"] = directions
        recipe["nutrients"] = nutrition_dict
        recipe["cooking_info"] = cooking_details
        recipe["link"] = response.request.meta["link"]

        yield recipe
