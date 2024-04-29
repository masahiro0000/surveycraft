from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('create/', views.create, name="create"),
    path('my-survey/', views.my_survey, name="my-survey"),
    path('survey-all/', views.survey_all, name="survey-all"),
    path('survey-answer/<int:pk>/', views.survey_answer, name="survey-answer"),
]