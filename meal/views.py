from django.shortcuts import render

from .models import Meal


def meals(request):

    return render(request, "meal/meals.html")
