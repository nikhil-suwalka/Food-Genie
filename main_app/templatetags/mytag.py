from django import template
register = template.Library()

@register.simple_tag
def dictKeyLookup(the_dict, key):
   # Try to fetch from the dict, and if it's not found return an empty string.
   if the_dict.get(key, "") == -1:
      return "No data"
   return the_dict.get(key, '') + " kcal"