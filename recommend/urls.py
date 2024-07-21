from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from . import views

urlpatterns = [
    #path((推荐页面的path), views.recommend),
    path("recommend/",views.recommemd)
]
