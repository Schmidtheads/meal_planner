from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django.http import JsonResponse, Http404
from django.forms import modelform_factory
import datetime
import calendar
import json

from .models import Meal
from .forms import MealForm as mealForm2
from recipe.models import Recipe
from cookbook.models import Cookbook


MealForm = modelform_factory(Meal, exclude=[])


def detail(request, id):
    '''
    This view is used to view/update meal details for a date that already has a meal assigned.
    '''

    meal = get_object_or_404(Meal, pk=id)

    if request.method == "POST":
        #form = MealForm(request.POST, instance=meal)
        form = mealForm2(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            return redirect("meals")
    else:
        
        # Create form for new or update entry - scheduled_date is uneditable
        #form = MealForm(instance=meal)
        form = mealForm2(instance=meal)
        scheduled_date_widget = form.fields['scheduled_date'].widget
        scheduled_date_widget.attrs['readonly'] = True
        # For consistent styling purposes assign form-control class to date widget to match readonly custom widget
        scheduled_date_widget.attrs.update({'class': 'form-control'})

    return render(request, "meal/detail.html",
                 {"title": "Meal Planner",
                  "year": datetime.datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "form": form})


def new(request):
    '''
    This view is used to assign a meal to a day which does not currently have one.
    The date is passed in as a URL query string with the syntax: ?date=YYYY-MM-DD
    '''

    if request.method == "POST":
        form = MealForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("meals")
    else:
        # Retrieve scheduled_date from query string value (must be YYYY-MM-DD format e.g. 2020-12-23)
        scheduled_date = request.GET.get('date', None)  # should default be current date?
        if not scheduled_date is None:
            # Check if date is valid
            try:
                date_obj = datetime.datetime.strptime(scheduled_date, "%Y-%m-%d")
                try:
                    meal = Meal.objects.get(scheduled_date=date_obj)

                    # if meal exists - need to redirect to details page (for update)
                except Meal.DoesNotExist:
                    meal = None
            except:
                # Invalid date, do not pre-populate the date on the form
                date_obj = None     
        else:
            date_obj = None

        # Create form for new entry
        if date_obj is None:
            form = MealForm() # create form without pre-populated date
        else:
            form = MealForm(initial={'scheduled_date': date_obj})
            scheduled_date_widget = form.fields['scheduled_date'].widget
            scheduled_date_widget.attrs['readonly'] = True
            # For consistent styling purposes assign form-control class to date widget to match readonly custom widget
            scheduled_date_widget.attrs.update({'class': 'form-control'})

    return render(request, "meal/detail.html",
                 {"title": "Meal Planner",
                  "year": datetime.datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "form": form})


def meals(request):
    '''
    This view is used to show the calendar view of meals.
    '''

    meals = serializers.serialize('json', Meal.objects.all())
    return render(request, 'meal/meals.html',
                  {'title': 'Meal Planner',
                   'meals': meals,
                   'year': datetime.datetime.now().year,
                   'company': 'Schmidtheads Inc.'})


def get_meals_for_month(request):
    
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
        meal_id = meal.id
        recipe = getattr(meal, 'recipe')
        # Get the recipe information
        name = getattr(recipe, 'name')
        page = getattr(recipe, 'page_number')
        cookbook = getattr(recipe, 'cook_book')

        # Get cookbook name and author
        cookbook_title = getattr(cookbook, 'title')
        cookbook_author = str(getattr(cookbook, 'author'))
        cookbook_id = cookbook.id

        # Create cookbook name abbreviation
        words = cookbook_title.split(' ')
        if len(words) == 1:
            cookbook_abbr = words[0][:3]
        else:
            cookbook_abbr = ''.join([w[0] for w in words])

        recipe_info = {'meal_id': meal_id, 'recipe_name': name, 'page': page, 'cookbook_id': cookbook_id, 'cookbook': cookbook_title, 'author': cookbook_author, 'abbr': cookbook_abbr}
    else:
        recipe_info = {'recipe_name': ''}

    return recipe_info


def _get_meal_id_by_date(date):
    '''
    '''

    # There should be only one meal per date, so only return first meal
    # object returned from filter.
    meal = Meal.objects.filter(scheduled_date=date).first()

    return meal


