from django.http import HttpResponse
from django.core import management
import threading
import os


# from .models import Ingredient, Recipe

# Create your views here.

def crawl():
    os.system('python manage.py crawl "paneer potato')
    # management.call_command('crawl', "paneer potato")



def homeview(request):
    # os.system('python manage.py crawl "paneer potato')

    t1 = threading.Thread(target=crawl)
    t1.start()
    # t1.join()

    # stream = os.popen('dir')
    # output = stream.read()
    # print(output)

    # management.call_command('crawl', "paneer potato")

    return HttpResponse()
