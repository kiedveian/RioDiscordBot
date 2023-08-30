import os
import random
from django.http import HttpResponse
from django.views.generic import TemplateView
# Create your views here.

# from rio.models import CloseTime

from Utility.MysqlManager import MysqlManager
from pages.StickerView import StickerPageView

# def home_page_view(request):
#     return HttpResponse("Hello, World!")


class HomePageView(TemplateView):
    template_name = "home.html"


class AbuotPageView(TemplateView):
    template_name = "about.html"


class Sticker1PageView(StickerPageView):
    pass
    template_name = "sticker1.html"
