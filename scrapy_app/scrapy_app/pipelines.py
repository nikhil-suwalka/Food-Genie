# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import neo4j


def getConnection():
    conn = neo4j.GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "nsuwalka"))
    return conn


def checkRecipe(tx, link):
    result = tx.run("MATCH (n:Recipe) where n.link = $link return ID(n) as id", link=link)
    return [r['id'] for r in result]


def createRecipe(tx, item):
    id = tx.run("CREATE (n:Recipe {name: $name,"
                "details:$details, "
                "ingredients:$ingredients,"
                "calories:$calories,"
                "directions:$directions,"
                "nutrients:$nutrients,"
                "preparation_time:$preparation_time, "
                "cooking_time:$cooking_time, "
                "total_time:$total_time, "
                "link:$link}) return n.identity as id",
                name=item["title"],
                details=item["details"],
                ingredients=item["ingredients"],
                calories=item["nutrients"]["total calories"],
                directions=item["directions"],
                nutrients=str(item["nutrients"]).replace('\'', '"'),
                preparation_time=item["cooking_info"]["prep"],
                cooking_time=item["cooking_info"]["cook"],
                total_time=item["cooking_info"]["total"],
                link=item["link"])


def checkIngredient(tx, ing):
    result = tx.run("MATCH (i:Ingredient {name: $name}) RETURN ID(i) as id", name=ing)
    return [r['id'] for r in result]


def createIngredient(tx, ing):
    result = tx.run("CREATE (n:Ingredient {name: $name}) return ID(n) as id", name=ing)


def createRelationship(tx, rid, iid):
    tx.run("MATCH (a:Recipe), (b:Ingredient) WHERE ID(a) = $rid AND ID(b) = $iid CREATE (a)-[r:CONTAINS]->(b)", rid=rid,
           iid=iid)


def addNewRecipe(conn, item):
    session = conn.session()
    recipes = session.read_transaction(checkRecipe, item["link"])
    if len(recipes) == 0:
        # create ingredients if not present
        iids = []

        for ing in item['ingredients']:
            result = session.read_transaction(checkIngredient, ing)

            if len(result) == 0:
                session.write_transaction(createIngredient, ing)
                print(session.read_transaction(checkIngredient, ing), "TEST")
                iid = session.read_transaction(checkIngredient, ing)[0]

                iids.append(iid)
                print("Created", ing)
            else:
                iids.append(result[0])
        # create recipe
        session.write_transaction(createRecipe, item)
        rid = session.read_transaction(checkRecipe, item['link'])[0]
        print("Created", item["title"])
        # create relation
        print("IDS", iids, rid)
        for iid in iids:
            session.write_transaction(createRelationship, rid, iid)


class ScrapyAppPipeline:
    def process_item(self, item, spider):
        conn = getConnection()
        addNewRecipe(conn, item)

        conn.close()
        return item
