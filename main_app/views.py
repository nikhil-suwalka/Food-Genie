import os
import subprocess
import threading

from django.http import HttpResponse

from .models import *
from neomodel import Q
import logging


# Create your views here.

def crawl(ingredients_list: list):
    # cmd = 'python manage.py crawl ' + ",".join(ingredients_list)
    os.system('python manage.py crawl ' + ",".join(ingredients_list))

    # with open(os.devnull, 'wb') as devnull:
    #     subprocess.check_call([cmd], stdout=devnull, stderr=subprocess.STDOUT)

    # process = subprocess.Popen([cmd],
    #                            stdout=subprocess.STDOUT,
    #                            stderr=subprocess.STDOUT)
    # stdout, stderr = process.communicate()
    # print(stderr)

    # os.system('python manage.py crawl "paneer potato"')
    # management.call_command('crawl', "paneer potato")


def addCombination(ingredients_list: list):
    ScrapedIngredients(combination=ingredients_list).save()


def combinationExists(ingredients_list: list) -> bool:
    try:
        result = ScrapedIngredients.nodes.get(combination=ingredients_list)
        return True
    except:
        return False


def getRecipesFromIngredients(ingredients_list: list):
    recipes_dict_count = {}
    recipes_dict_ob = {}

    for ingr in ingredients_list:
        i = Ingredient.nodes.filter(Q(name__contains=ingr))
        recipes = i.recipe
        id_selected = dict()
        for r in recipes:
            if not id_selected.get(r.id, False):
                recipes_dict_count[r.id] = recipes_dict_count.get(r.id, 0) + 1
                recipes_dict_ob[r.id] = r
                id_selected[r.id] = True

    # sorted_recipes = sorted(recipes_dict_count.items(), key=lambda x: x[1], reverse=True)
    # print(sorted_recipes)
    counter = {}
    for i in recipes_dict_count.items():
        counter[i[1]] = counter.get(i[1], []) + [i[0]]
    sorted_recipes = sorted(counter.items(), key=lambda x: x[0], reverse=True)

    # maximum = max(sorted_recipes, key=lambda x: x[1])[1]
    # print(maximum)
    return sorted_recipes, recipes_dict_ob


# Fetch recipes from database and scrape if needed
def fetchRecipes(ingredients_list: list, all_ingredient_recipes: int, return_recipe_count: int) -> list:
    ingredients_list.sort()
    counter, objects = getRecipesFromIngredients(ingredients_list)
    print(f"Found {len(counter[0][1]) if counter else 0} recipes in database with all required ingredients")

    # If NOT ( number of recipes found are having all the ingredients and at least (all_ingredient_recipes) recipes
    # are there and total recipes found are at least (return_recipe_count))
    if not (counter and counter[0][0] == len(ingredients_list) and len(counter[0][1]) >= all_ingredient_recipes and sum(
            [len(x[1]) for x in counter])):
        if not combinationExists(ingredients_list):
            print("Scraping")
            t1 = threading.Thread(target=crawl, args=([ingredients_list]))
            t1.start()
            t1.join()
            addCombination(ingredients_list)
            counter, objects = getRecipesFromIngredients(ingredients_list)

        # TODO: Scrap combinations
    else:
        print("Skipping scraping")
    recipes = [objects[x] for x in counter[0][1]]
    for i in range(1, len(counter)):
        recipes.extend([objects[x] for x in counter[i][1]])
        if len(recipes) >= return_recipe_count:
            return recipes[:return_recipe_count]
    return recipes[:return_recipe_count]


def homeview(request):
    if request.method == "GET":
        ingredients = request.GET.getlist("ingredients")
        print(ingredients)
        if ingredients:
            recipes = fetchRecipes(ingredients, 8, 15)
            print("Found ", len(recipes), "recipes")
            for i in range(len(recipes)):
                print(f"{i+1}: {recipes[i].name}")
    # print(logging.getLogger(__name__))
    # else:
    # t1 = threading.Thread(target=crawl, args=([["chicken"]]))
    # t1.start()
    # t1.join()

    return HttpResponse()
