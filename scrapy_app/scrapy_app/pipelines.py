# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter
import neo4j
import hashlib


def getConnection():
    conn = neo4j.GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "pass"))
    return conn


def checkRecipe(tx, link):
    print("LINK", link)
    result = tx.run("MATCH (n:Recipe) where n.link = $link return n.name as name",link=link)
    return [r['name'] for r in result]


def createRecipe(tx, item):
    tx.run("CREATE (n:Recipe {name: $name,"
           "details:$details, " 
           "ingredients:$ingredients," 
           "calories:$calories," 
           "directions:$directions," 
           "nutrients:$nutrients," 
           "preparation_time:$preparation_time, " 
           "cooking_time:$cooking_time, " 
           "total_time:$total_time, " 
           "link:$link})",
           name=item["title"],
           details=item["details"],
           ingredients=item["ingredients"],
           calories=item["nutrients"]["total calories"],
           directions=item["directions"],
           nutrients=str(item["nutrients"]).replace('\'', '"'),
           preparation_time=item["cooking_info"]["prep:"],
           cooking_time=item["cooking_info"]["cook:"],
           total_time=item["cooking_info"]["total:"],
           link=item["link"])


def checkIngredient(tx, ing):
    result = tx.run("MATCH (i:Ingredient {name: $name}) RETURN i.name as name", name=ing)
    return [r['name'] for r in result]


def createIngredient(tx, ing):
    tx.run("CREATE (n:Ingredient {name: $name})", name=ing)


def addNewRecipe(conn, item):
    results = []
    session = conn.session()
    recipes = session.read_transaction(checkRecipe, item["link"])
    if len(results) == 0:
        # create ingredients if not present
        for ing in item['ingredients']:
            result = session.read_transaction(checkIngredient, ing)

            if len(result) == 0:
                session.write_transaction(createIngredient, ing)
                print("Created", ing)

        # create recipe
        session.write_transaction(createRecipe, item)
        print("Created", item["title"])
        # create relation


class ScrapyAppPipeline:
    def process_item(self, item, spider):
        conn = getConnection()
        addNewRecipe(conn, item)

        conn.close()
        return item
