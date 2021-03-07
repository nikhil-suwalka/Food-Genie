from django.db import models
from neomodel import StructuredNode, StringProperty, DateProperty, IntegerProperty, UniqueIdProperty, ArrayProperty, \
    JSONProperty, FloatProperty, RelationshipTo


# Create your models here.
class Recipe(StructuredNode):
    recipe_id = UniqueIdProperty()
    name = StringProperty(required=True)
    details = StringProperty(required=True)
    ingredients = ArrayProperty(base_property=StringProperty(), required=True)
    calories = FloatProperty(required=True)
    directions = ArrayProperty(base_property=StringProperty(), required=True)
    nutrients = JSONProperty(required=True)
    preparation_time = StringProperty(required=True)
    cooking_time = StringProperty(required=True)
    total_time = StringProperty(required=True)
    link = StringProperty(required=True)

    class Meta:
        verbose_name = "Recipe details"

class Ingredient(StructuredNode):
    ingredient_id = UniqueIdProperty()
    name = StringProperty(required=True)
    recipe = RelationshipTo(Recipe, "is_in")

    class Meta:
        verbose_name = "Ingredients of a recipe"



