from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse 
import datetime
import calendar
import json

from .models import Meal
from recipe.models import Recipe
from cookbook.models import Cookbook


def meals(request):
    meals = serializers.serialize('json', Meal.objects.all())
    return render(request, 'meal/meals.html',
                  {'title': 'Meal Planner',
                   'meals': meals,
                   'year': datetime.datetime.now().year,
                   'company': 'Schmidtheads Inc.'})


def meals_for_month(request):
    
    meal_year = int(request.GET.get('year', datetime.datetime.now().year))
    meal_month = int(request.GET.get('month', datetime.datetime.now().month)) 

    meals_json = _get_meals_for_month(meal_year, meal_month)

    data = {
        'month_meals': meals_json
    }

    return JsonResponse(data)


def _get_meals_for_month(year, month):

    meals_for_month = Meal.objects.filter(
        scheduled_date__year=year,
        scheduled_date__month=month).order_by('scheduled_date')

    meals_info = []
    days_in_month = calendar.monthrange(year, month)[1]
    for day in range(1, days_in_month+1):
        check_date = f'{year}-{month}-{day}'
        meal = meals_for_month.filter(scheduled_date = datetime.date(year, month, day)).first()

        meal_info = {'scheduled_date': check_date}
        meal_info.update(_get_recipe_info_for_meal(meal))

        meals_info.append(meal_info)
            
    return meals_info


def _get_recipe_info_for_meal(meal):

    if not meal is None:
        recipe = getattr(meal, 'recipe')
        # Get the recipe information
        name = getattr(recipe, 'name')
        page = getattr(recipe, 'page_number')
        cookbook = getattr(recipe, 'cook_book')

        # Get the cookbook name
        cookbook_title = getattr(cookbook, 'title')

        # Create cookbook name abbreviation
        words = cookbook_title.split(' ')
        if len(words) == 1:
            cookbook_abbr = words[0][:3]
        else:
            cookbook_abbr = ''.join([w[0] for w in words])

        recipe_info = {'recipe_name': name, 'page': page, "cookbook": cookbook_title, "abbr": cookbook_abbr}
    else:
        recipe_info = {'recipe_name': ''}

    return recipe_info

