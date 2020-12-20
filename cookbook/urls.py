from django.urls import path

from . import views


urlpatterns = [
    path('<int:id>', views.detail, name='cookbook_detail'),
    path('list', views.cookbooks, name='cookbooks'),
]



