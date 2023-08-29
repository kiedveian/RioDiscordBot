from django.urls import path

# from .views import home_page_view
from .views import AbuotPageView, HomePageView, Sticker1PageView

urlpatterns = [
    # path("", home_page_view, name="home"),
    path("sticker1/", Sticker1PageView.as_view(), name="sticker1"),
    path("about/", AbuotPageView.as_view(), name="about"),
    path("", HomePageView.as_view(), name="home"),
]
