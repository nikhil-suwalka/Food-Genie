import os
import threading

from django.http import HttpResponse

from .models import Ingredient, Recipe


# Create your views here.

def crawl():
    os.system('python manage.py crawl "chicken"')
    # os.system('python manage.py crawl "paneer potato"')
    # management.call_command('crawl', "paneer potato")


def homeview(request):
    t1 = threading.Thread(target=crawl)
    t1.start()
    t1.join()

    return HttpResponse()


def retrieve(request):
    # all = Ingredient.nodes.all()
    all = Ingredient.nodes.get(name='chicken')
    print(all)
    return HttpResponse()

