from django.urls import path

from . import views


urlpatterns = [
    path('meals', views.meals, name='meals'),
    path('meals_by_month', views.meals_for_month, name='meals_by_month'),
]

