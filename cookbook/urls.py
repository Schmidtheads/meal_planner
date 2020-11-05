from django.urls import path

from . import views


urlpatterns = [
    path('<int:id>', views.detail, name='detail'),
    path('list', views.cookbooks, name='cookbooks'),
]

