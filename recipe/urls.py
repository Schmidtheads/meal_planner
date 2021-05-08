from django.urls import path

from . import views


urlpatterns = [
    path('<int:id>', views.detail, name='recipe_detail'),
    path('list', views.recipes, name='recipes'),
]
