from django.urls import path

from . import views


urlpatterns = [
    path('meals', views.meals, name='meals'),
    path('<int:id>', views.detail, name='meal_detail'),
    path('new', views.new, name='new_meal'),
    path('meals_by_month', views.get_meals_for_month, name='meals_by_month'),
    path('recipe_search', views.search_for_recipes, name='recipe_search'),
    path('print', views.PrintCreatePopup, name='print'),
]
