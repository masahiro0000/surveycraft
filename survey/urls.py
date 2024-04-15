from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('surveys/', views.surveys, name="surveys"),
    path('create/', views.create, name="create"),
    path('my-survey/', views.my_survey, name="my-survey"),
]