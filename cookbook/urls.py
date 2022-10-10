from django.urls import path

from . import views


urlpatterns = [
    path('<int:id>', views.detail, name='cookbook_detail'),
    path('list', views.cookbooks, name='cookbooks'),
    path('new', views.new, name='cookbook_new'),
    path('author/create', views.AuthorCreatePopup, name='author_create'),
    path('author/<int:id>/edit', views.AuthorEditPopup, name='author_edit'),
]