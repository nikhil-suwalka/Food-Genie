import scrapy
import logging


class RecipeItem(scrapy.Item):
    ingredient = scrapy.Field()


class RecipeSpider(scrapy.Spider):
    name = "RecipeFetcher"
    allowed_domains = ['www.allrecipes.com']
    rec = ["paneer", "potato"]
    link = "https://www.allrecipes.com/search/results/?ingIncl="
    for i in range(len(rec)):
        link += rec[i]
        link += ","
    start_urls = [link[:-1]]

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
                                 meta={"title": title[i], "details": details[i]})

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

        yield {
            "title": response.request.meta["title"],
            "details": response.request.meta["details"],
            "ingredients": ingredients,
            "directions": directions,
            "nutrients": nutrition_dict,
            "cooking_info": cooking_details
        }
