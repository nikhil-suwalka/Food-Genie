import json
import os
import threading

from django.http import HttpResponse
from django.shortcuts import render
from neomodel import Q

from .models import *


# Create your views here.

def crawl(ingredients_list: list, excludes: list):
    # cmd = 'python manage.py crawl ' + ",".join(ingredients_list)

    inc = ",".join(ingredients_list)
    inc = inc.replace(" ", "_")

    if excludes:
        exc = ",".join(excludes)
        exc = exc.replace(" ", "_")
        os.system('python manage.py crawl --includes ' + inc + " --excludes " + exc)
    else:
        os.system('python manage.py crawl --includes ' + inc)

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
    # counter = {}
    # for i in recipes_dict_count.items():
    #     counter[i[1]] = counter.get(i[1], []) + [i[0]]
    # sorted_recipes = sorted(counter.items(), key=lambda x: x[0], reverse=True)

    # maximum = max(sorted_recipes, key=lambda x: x[1])[1]
    # print(maximum)
    return recipes_dict_count, recipes_dict_ob


# Fetch $return_recipe_count recipes from database with at least $all_ingredient_recipes recipes with all the
# ingredients and scrape if needed
def fetchRecipes(ingredients_list: list, excluded_ingredients: list, all_ingredient_recipes: int,
                 return_recipe_count: int, calorie_slider: float) -> list:
    ingredients_list.sort()
    recipes_dict_count, objects = getRecipesFromIngredients(ingredients_list)

    if excluded_ingredients:
        temp, objects_excludes = getRecipesFromIngredients(excluded_ingredients)

        i = 0
        while i < len(objects):
            if list(objects.keys())[i] in objects_excludes:
                del objects[list(objects.keys())[i]]
            else:
                i += 1

    counter = {}
    for i in recipes_dict_count.items():
        if i[0] in objects:
            counter[i[1]] = counter.get(i[1], []) + [i[0]]
    counter = sorted(counter.items(), key=lambda x: x[0], reverse=True)

    if counter and counter[0][0] == len(ingredients_list):
        print(f"Found {len(counter[0][1]) if counter else 0} recipes in database with all required ingredients")

    print("Total recipes found: ", sum([len(x[1]) for x in counter]))

    # If NOT ( number of recipes found are having all the ingredients and at least (all_ingredient_recipes) recipes
    # are there and total recipes found are at least (return_recipe_count))
    if not (counter and counter[0][0] == len(ingredients_list) and len(counter[0][1]) >= all_ingredient_recipes and sum(
            [len(x[1]) for x in counter]) >= return_recipe_count):

        # Same combination have not been scraped before
        if not combinationExists(ingredients_list):
            print("Scraping")
            t1 = threading.Thread(target=crawl, args=([ingredients_list, excluded_ingredients]))
            t1.start()
            t1.join()
            addCombination(ingredients_list)
            recipes_dict_count, objects = getRecipesFromIngredients(ingredients_list)
            counter = {}
            for i in recipes_dict_count.items():
                if i[0] in objects:
                    counter[i[1]] = counter.get(i[1], []) + [i[0]]
            counter = sorted(counter.items(), key=lambda x: x[0], reverse=True)
        # TODO: Scrap combinations
    else:
        print("Skipping scraping")
    if objects:
        recipes = [objects[x] for x in counter[0][1]]
        for i in range(1, len(counter)):
            recipes.extend([objects[x] for x in counter[i][1]])
        print("Hello", recipes[:return_recipe_count][0].calories)
        recipes = [recipe for recipe in recipes if recipe.calories <= calorie_slider]
        return recipes[:return_recipe_count]
    return []


def getRecipesWithoutExcludes(recipes, excludes):
    for recipe in recipes:
        id = recipe.id


def homeview(request):
    # http://127.0.0.1:8000/?ingredients=chicken&ingredients=cheese

    # if request.method == "GET":
    #     ingredients = request.GET.getlist("ingredients")
    #     print(ingredients)
    #     if ingredients:
    #         recipes = fetchRecipes(ingredients, 8, 15)
    #         print("Showing ", len(recipes), "recipes")
    #         for i in range(len(recipes)):
    #             print(f"{i + 1}: {recipes[i].name}")
    # print(logging.getLogger(__name__))
    # else:
    # t1 = threading.Thread(target=crawl, args=([["chicken"]]))
    # t1.start()
    # t1.join()

    return render(request, "index.html", {})


def fetch(request):
    if request.method == "POST":
        tags = json.loads(request.POST.get("tags"))
        allowed_list = json.loads(request.POST.get("allowed_list"))
        calorie_slider = request.POST.get("calorie_slider")

        includes = []
        excludes = []
        for i in range(len(tags)):
            if allowed_list[i] == 1:
                includes.append(tags[i])
            else:
                excludes.append(tags[i])

        print(includes, excludes)
        recipes = fetchRecipes(includes, excludes, 8, 15, float(calorie_slider))
        print("Showing ", len(recipes), "recipes")

        for i in range(len(recipes)):
            print(f"{i + 1}: {recipes[i].name}")
            print(recipes[i])
        recipes_list = [
            {"id": x.id, "name": x.name, "ingredients": x.ingredients, "details": x.details, "directions": x.directions,
             "nutrients": x.nutrients, "preparation_time": x.preparation_time, "cooking_time": x.cooking_time,
             "total_time": x.total_time, "image_path": x.image_path if x.image_path else '/static/img/default.png', "view_count": x.view_count} for x in recipes]
        return HttpResponse(json.dumps({"recipes": recipes_list}), content_type="application/json")


def items(request):

    if request.method == "POST":
        if request.POST.get("view"):
            recipes = json.loads(request.POST.get("view"))
            recipes = sorted(recipes, key=lambda x: x["view_count"], reverse=True)
            raw = request.POST.get("view")

        elif request.POST.get("match"):
            recipes = json.loads(request.POST.get("match"))
            raw = request.POST.get("match")

        elif request.POST.get("calorie"):
            recipes = json.loads(request.POST.get("calorie"))

            recipes = sorted(recipes, key=lambda x: x["nutrients"]["total calories"])
            raw = request.POST.get("calorie")

        else:
            print("here")
            recipes = json.loads(request.POST.get("recipes"))
            raw = request.POST.get("recipes")
            print("RAW", raw)

    return render(request, "items.html", {"recipes": recipes, "recipe_json": raw})


def recipe(request):
    recipe_id = request.GET.get("id")
    r = Recipe.nodes.get(name=recipe_id)
    r.view_count += 1
    if r.image_path is None:
        r.image_path = '/static/img/default.png'
    r.save()
    return render(request, "recipe.html", {"recipe": r})
