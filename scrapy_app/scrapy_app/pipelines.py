# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import neo4j
import spacy, re
from fuzzywuzzy import process
nlp = spacy.load('en_core_web_sm')


def getMatches(str2Match: str, strOptions: list):
    highest = process.extractOne(str2Match, strOptions, score_cutoff=80)
    return highest[0] if highest else None


def _filter(token):
    if len(token) < 2:
        return False
    if token.is_stop:
        return False
    if token.is_digit:
        return False
    if token.like_num:
        return False
    return True

def getProcessedIngredients(ingredient):
    blacklist = ["cup", "teaspoon", "teaspoons", "cups", "tablespoons", "tablespoon", "medium", "large", "small",
                 "ounce",
                 "ounces", "cube", "cubes", "inch", "inches", "pound", "pounds", "cubed", "piece", "pieces", "halves"]

    ingredient = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", ingredient)
    # ingredient = ingredient.split(",")[0]
    var = nlp(ingredient)
    ingr = []
    for token in var:
        if str(token) not in blacklist and _filter(token):
            ingr.append(str(token))
        # print(token, token.tag_, token.pos_, spacy.explain(token.tag_))
    return ingr

def getConnection():
    conn = neo4j.GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "pass"))
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
            # result = session.read_transaction(checkIngredient, ing)
            processed_ings = getProcessedIngredients(ing)
            db_ings = getMatchedIngredients(conn,processed_ings)
            ing = " ".join(processed_ings)
            matched_ing = getMatches(ing, list(db_ings.keys()))
            if len(db_ings) == 0 or not matched_ing:
                session.write_transaction(createIngredient,ing)
                # print(session.read_transaction(checkIngredient, ing), "TEST")
                iid = session.read_transaction(checkIngredient, ing)[0]
                iids.append(iid)
                print("Created", ing)
            else:
                iids.append(db_ings[matched_ing])
        # create recipe
        session.write_transaction(createRecipe, item)
        rid = session.read_transaction(checkRecipe, item['link'])[0]
        print("Created", item["title"])
        # create relation
        print("IDS", iids, rid)
        for iid in iids:
            session.write_transaction(createRelationship, rid, iid)

def containIngredientKeyword(tx,ing):
    result = tx.run("MATCH (i:Ingredient) WHERE i.name CONTAINS $ing return i as ingredient",ing=ing)
    return {r['ingredient']['name']:r['ingredient'].id for r in result}

def getMatchedIngredients(conn,ings):
    iids = {}
    session = conn.session()
    for ing in ings:
        recipes = session.read_transaction(containIngredientKeyword, ing)
        iids.update(recipes)
    return iids


class ScrapyAppPipeline:
    def process_item(self, item, spider):
        conn = getConnection()
        addNewRecipe(conn, item)
        conn.close()
        return item
