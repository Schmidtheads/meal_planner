from django.urls import path

from . import views


urlpatterns = [
    path('<int:id>', views.detail, name='recipe_detail'),
    path('list', views.recipes, name='recipes'),
    path('new', views.new, name='recipe_new'),
    path('recipe_type/create', views.RecipeTypeCreatePopup, name='recipe_type_create'),
    path('<int:recipe_id>/recipe_ratings', views.ratings_list, name='recipe_rating_list'),
    path('<int:recipe_id>/recipe_ratings/rating', views.update_rating, name='rating_new'),
]
