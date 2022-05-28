from django.urls import path
from . import views

urlpatterns=[
    path('home/',views.home,name="home"),
    path('similarity/',views.similarity,name="similarity"),
    path('recommend/',views.recommend,name="recommend")
]