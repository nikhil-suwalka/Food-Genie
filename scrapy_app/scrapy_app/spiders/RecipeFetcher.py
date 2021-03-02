import scrapy
import logging
from ..items import RecipeItem


class RecipeSpider(scrapy.Spider):
    name = "RecipeFetcher"
    allowed_domains = ['www.allrecipes.com']

    def __init__(self, ingredients=None, **kwargs):
        ingredients = ingredients.split()
        # rec = ["paneer", "potato"]

        link = "https://www.allrecipes.com/search/results/?ingIncl="
        for i in range(len(ingredients)):
            link += ingredients[i]
            link += ","

        self.start_urls = [link[:-1]]

        super().__init__(**kwargs)

    # start_urls = ["https://www.allrecipes.com/search/results/?ingIncl=paneer,potato&sort=re"]

    def parse(self, response, **kwargs):
        title = response.xpath("//h3/a/span/text()").getall()
        links = response.xpath("//h3/a/@href").getall()
        details = response.xpath("//a/div[@class='fixed-recipe-card__description']/text()").getall()
        for i in range(len(links)):
            # yield {
            #     "title": title[i],
            #     "details": details[i],
            #     "link": links[i],
            # }

            yield scrapy.Request(url=links[i], callback=self.parse_links,
                                 meta={"title": title[i], "details": details[i], "link": links[i]})

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
            # print("qwertyuiop",nutrition.xpath("span[1]/text()").get().strip())
            # print("qwertyuiop",nutrition.xpath("span[1]/span[2]/text()").get().strip())
            nutrition_dict[nutrition.xpath("span[1]/text()").get().strip()] = nutrition.xpath(
                "span[1]/span[2]/text()").get().strip()

        cooking_details = {}
        cookings = response.xpath("//section[@class='recipe-meta-container two-subcol-content clearfix']/div[1]/div")
        for cooking in cookings:
            cooking_details[cooking.xpath("div[1]/text()").get().strip()] = cooking.xpath("div[2]/text()").get().strip()

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

        # recipe["name"] = response.request.meta["title"]
        # recipe["details"] = response.request.meta["details"]
        # recipe["ingredients"] = ingredients
        # recipe["calories"] = nutrition_dict["total calories"]
        # recipe["directions"] = directions
        # recipe["nutrients"] = nutrition_dict
        # recipe["preparation_time"] = cooking_details[0]
        # recipe["cooking_time"] = cooking_details[1]
        # recipe["total_time"] = cooking_details[2]
        # recipe["link"] = response.request.meta["link"]

        yield recipe

        # yield {
        #     "title": response.request.meta["title"],
        #     "details": response.request.meta["details"],
        #     "link": response.request.meta["link"],
        #     "ingredients": ingredients,
        #     "directions": directions,
        #     "nutrients": nutrition_dict,
        #     "cooking_info": cooking_details
        # }
