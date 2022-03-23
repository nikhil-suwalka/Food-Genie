import scrapy
import logging
from ..items import RecipeItem


class RecipeSpider(scrapy.Spider):
    name = "RecipeFetcher"
    allowed_domains = ['www.allrecipes.com']

    def __init__(self, ingredients=None, excludes=None, **kwargs):
        ingredients = ingredients.replace("_", " ")
        ingredients = ingredients.split(",")

        # rec = ["paneer", "potato"]

        link = "https://www.allrecipes.com/search/results/?"
        for i in range(len(ingredients)):
            link += "&IngIncl="
            link += ingredients[i]

        if excludes:
            excludes = excludes.replace("_", " ")
            excludes = excludes.split(",")
            for i in range(len(excludes)):
                link += "&IngExcl="
                link += excludes[i]

        # self.start_urls = [link[:-1]+"&sort=re"]
        self.start_urls = [link]

        super().__init__(**kwargs)

    def parse(self, response, **kwargs):

        # NEW
        title = response.xpath("//div/div/div/a/h3[@class='card__title elementFont__resetHeading']/text()").getall()
        links = response.xpath(
            "//div[@class='component card card__recipe card__facetedSearchResult']/div/div/a/@href").getall()
        details = response.xpath(
            "//div[@class='component card card__recipe card__facetedSearchResult']/div/div/div[@class='card__summary elementFont__details--paragraphWithin margin-8-tb']/text()").getall()

        print("title", title, len(title))
        print("LINKS", links, len(links))
        print("details", details, len(details))
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

        ingredients = response.xpath(
            "//label/span/span[@class='ingredients-item-name elementFont__body']/text()").getall()
        ingredients = [x.strip() for x in ingredients]
        directions = response.xpath("//li/div/div/p/text()").getall()
        directions = [x for x in directions]

        nutrition_dict = {}

        nutrition_dict["total calories"] = response.xpath(
            "//div[@class='nutrition-top light-underline elementFont__subtitle']/span/following-sibling::text()").get()
        if nutrition_dict["total calories"]:
            nutrition_dict["total calories"] = nutrition_dict["total calories"].strip()
        else:
            nutrition_dict["total calories"] = -1
        nutritions = response.xpath("//div[@class='nutrition-body elementFont__details']/div")

        for nutrition in nutritions:
            nutrition_dict[nutrition.xpath("span[1]/text()").get().strip()] = nutrition.xpath(
                "span[1]/span[2]/text()").get()
            if nutrition_dict[nutrition.xpath("span[1]/text()").get().strip()]:
                nutrition_dict[nutrition.xpath("span[1]/text()").get().strip()] = nutrition_dict[
                    nutrition.xpath("span[1]/text()").get().strip()].strip()

        cooking_details = {}
        cookings = response.xpath(
            "//section[@class='recipe-meta-container two-subcol-content clearfix recipeMeta']/div[1]/div")
        for cooking in cookings:
            cooking_details[cooking.xpath("div[1]/text()").get().strip().split(':')[0]] = cooking.xpath(
                "div[2]/text()").get()
            if cooking_details[cooking.xpath("div[1]/text()").get().strip().split(':')[0]]:
                cooking_details[cooking.xpath("div[1]/text()").get().strip().split(':')[0]] = cooking_details[
                    cooking.xpath("div[1]/text()").get().strip().split(':')[0]].strip()

        recipe = RecipeItem()

        for item in ["prep", "cook", "total"]:
            if item not in cooking_details:
                cooking_details[item] = "N/A"

        recipe["image_path"] = response.xpath('//div[@class="image-container"]/div/@data-src').get()

        if recipe["image_path"]:
            recipe["image_path"] = recipe["image_path"].strip()
        else:
            recipe["image_path"] = None

        recipe["title"] = response.request.meta["title"]
        recipe["details"] = response.request.meta["details"]
        recipe["ingredients"] = ingredients
        recipe["directions"] = directions
        recipe["nutrients"] = nutrition_dict
        recipe["cooking_info"] = cooking_details
        recipe["link"] = response.request.meta["link"]

        yield recipe
