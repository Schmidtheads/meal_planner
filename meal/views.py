'''
Name: views.py
Description: Django views for Recipe object
Author: M. Schmidt
'''

import calendar
from datetime import datetime, date
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import io

from .calendar_report import MonthlyMealPlan
from recipe.search import Search
from .models import Meal
from .forms import MealForm, PrintForm


def detail(request, id):
    '''
    This view is used to view/update meal details for a date that already has a meal assigned.
    '''

    meal = get_object_or_404(Meal, pk=id)

    if request.method == "POST":
        form = MealForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            return redirect("meals")
    else:
        # Create form for new or update entry - scheduled_date is uneditable
        form = MealForm(instance=meal)

    scheduled_date_widget = form.fields['scheduled_date'].widget
    scheduled_date_widget.attrs['readonly'] = True
    # For consistent styling purposes assign form-control class to date widget to match readonly custom widget
    scheduled_date_widget.attrs.update({'class': 'form-control'})

    return render(request, "meal/detail.html",
                  {"title": "Meal Planner",
                   "year": datetime.now().year,
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
            # If form is not valid make sure that date stays read only
            scheduled_date_widget = form.fields['scheduled_date'].widget
            scheduled_date_widget.attrs['readonly'] = True
            # For consistent styling purposes assign form-control class to date widget to match readonly custom widget
            scheduled_date_widget.attrs.update({'class': 'form-control'})
    else:
        # Retrieve scheduled_date from query string value (must be YYYY-MM-DD format e.g. 2020-12-23)
        # should default be current date?
        scheduled_date = request.GET.get('date', None)
        if not scheduled_date is None:
            # Check if date is valid
            try:
                date_obj = datetime.strptime(
                    scheduled_date, "%Y-%m-%d")
                try:
                    _ = Meal.objects.get(scheduled_date=date_obj)

                    # if meal exists - need to redirect to details page (for update)
                except Meal.DoesNotExist:
                    print('Meal not found!')
            except:
                # Invalid date, do not pre-populate the date on the form
                date_obj = None
        else:
            date_obj = None

        # Create form for new entry
        if date_obj is None:
            form = MealForm()  # create form without pre-populated date
        else:
            form = MealForm(initial={'scheduled_date': date_obj})
            scheduled_date_widget = form.fields['scheduled_date'].widget
            scheduled_date_widget.attrs['readonly'] = True
            # For consistent styling purposes assign form-control class to date widget to match readonly custom widget
            scheduled_date_widget.attrs.update({'class': 'form-control'})

    return render(request, "meal/detail.html",
                  {"title": "Meal Planner",
                   "year": datetime.now().year,
                   "company": "Schmidtheads Inc.",
                   "form": form})


def meals(request):
    '''
    This view is used to show the calendar view of meals.
    '''

    # Don't need to pass any meal information in as when the meal calendar
    # loads, it will send an Ajax request to retrieve the meals
    return render(request, 'meal/meals.html',
                  {'title': 'Meal Planner',
                   'year': datetime.now().year,
                   'company': 'Schmidtheads Inc.'})



def PrintCreatePopup(request):

    if request.method == "POST":
        form = PrintForm(request.POST)
        meal_yr = int(form['meal_year'].data)
        meal_mt = int(form['meal_month'].data)
        print_flag = form['print_weeks'].data
        print_wks = form['weeks'].data
        print_only_meals = form['print_only_meals'].data

        meal_yr_mnth = f'{meal_yr}-{meal_mt:02}'
        if print_flag == 'ALL':
            print_weeks = [1,2,3,4,5]
        else:
            print_weeks = [int(w) for w in print_wks]

        # Get meals for the previous and next month too!
        prev_year, prev_month = _get_previous_month_and_year(meal_yr, meal_mt)
        next_year, next_month = _get_next_month_and_year(meal_yr, meal_mt)
        prev_month_meals = _get_meals_for_month(prev_year, prev_month)
        month_meals = _get_meals_for_month(meal_yr, meal_mt)
        next_month_meals = _get_meals_for_month(next_year, next_month)
        meals = prev_month_meals + month_meals + next_month_meals

        mmp = MonthlyMealPlan(meal_yr_mnth, meals, print_weeks, print_only_meals)
        mmp.output_filepath = f'MealPlan-{meal_yr}-{meal_mt:02}.pdf'
        mmp.output_type = 'S'
        pdf_bytestring = io.BytesIO(mmp.print_page())
   
        return FileResponse(pdf_bytestring, 
            content_type='application/pdf', 
            filename=f'MealPlan-{meal_yr}-{meal_mt:02}.pdf'
            )
 
    else:
        form = PrintForm()

    return render(request, "meal/print.html",
                  {"year": datetime.now().year,
                   "company": "Schmidtheads Inc.",
                   "form": form,
                   "meal_month": 0,
                   "meal_year": 0})


def get_meals_for_month(request):
    '''
    Handle query request from web application to get meals for a given month

    @param request: json representing the query; consists of year as 4 digit year
                    and month as 2 digit month
    @return json response string
    '''

    meal_year = int(request.GET.get('year', datetime.now().year))
    meal_month = int(request.GET.get('month', datetime.now().month))

    meals_json = _get_meals_for_month(meal_year, meal_month)

    data = {
        'month_meals': meals_json
    }

    return JsonResponse(data)


def search_for_recipes(request):
    '''
    Handle query request from web application to get recipes base on search criteria

    @param request: json representing the query; list of search tags
    '''

    search_keys = str(request.GET.get('keys'))
    results = _search_for_recipes(search_keys)

    data = {
        'recipes': results
    }

    return JsonResponse(data)


def _get_meals_for_month(year: int, month: int):
    '''
    Helper function that gathers meal information for a month from database

    @param year: 4 digit year
    @param month: 2 digit month
    @return Python List of meals for month; each item in list
            is a Python dictionary of meal information
    '''

    meals_for_month = Meal.objects.filter(
        scheduled_date__year=year,
        scheduled_date__month=month).order_by('scheduled_date')

    meals_info = []
    days_in_month = calendar.monthrange(year, month)[1]
    for day in range(1, days_in_month+1):
        check_date = f'{year}-{month:02}-{day:02}'
        meal = meals_for_month.filter(
            scheduled_date=date(year, month, day)).first()

        meal_info = {'scheduled_date': check_date}
        meal_info.update(_get_recipe_info_for_meal(meal))

        meals_info.append(meal_info)

    return meals_info


def _get_recipe_info_for_meal(meal):
    '''
    Helper function to get recipe information for a given meal

    @param meal: a Meal object
    @return Python dictionary of reciped information (name, page, cookbook, author)
    '''

    if not meal is None:
        meal_id = meal.id
        recipe = getattr(meal, 'recipe')
        # Get the recipe information
        name = getattr(recipe, 'name')
        page = getattr(recipe, 'page_number')
        cookbook = getattr(recipe, 'cook_book')

        # Get cookbook name and author
        if cookbook is not None:
            cookbook_title = getattr(cookbook, 'title')
            cookbook_author = str(getattr(cookbook, 'author'))
            cookbook_id = cookbook.id

            # Create cookbook name abbreviation
            words = cookbook_title.split(' ')
            if len(words) == 1:
                cookbook_abbr = words[0][:3]
            else:
                cookbook_abbr = ''.join([w[0] for w in words])
        else:
            # If no cookbook associated with the recipe then cookbook is "Unknown"
            cookbook_title = 'Unknown'
            cookbook_abbr = 'Unk'
            cookbook_author = 'Unknown'
            cookbook_id = 0

        recipe_info = {
            'meal_id': meal_id,
            'recipe_name': name,
            'page': page,
            'cookbook_id': cookbook_id,
            'cookbook': cookbook_title,
            'author': cookbook_author,
            'abbr': cookbook_abbr
        }
    else:
        recipe_info = {'recipe_name': ''}

    return recipe_info


def _search_for_recipes(search_keys):

    # Call serach object
    # TEST SEARCH
    srch = Search(search_keys)
    recipe_result = srch.find()

    result_list = []
    for recipe in recipe_result:

        # get last time recipe was made
        last_made_date = _date_recipe_last_made(recipe)
        times_made = _number_of_times_recipe_made(recipe)

        cb = recipe.cook_book
        cb_title = '' if cb is None else cb.title
        author = None if cb is None else cb.author
        author_fn = '' if author is None else author.first_name
        author_ln = '' if author is None else author.last_name
        candidate = {
            'id': recipe.id,
            'name': recipe.name,
            'cookbook': cb_title,
            'author': f'{author_fn} {author_ln}',
            'last made': last_made_date,
            'rating': recipe.rating(),
            'times made': times_made
        }
        result_list.append(candidate)

    return result_list


def _date_recipe_last_made(recipe):
    '''
    Returns when the recipe was last made
    '''

    meals_w_recipe = Meal.objects.filter(recipe = recipe).order_by("-scheduled_date")

    # meals sorted by date made (descending), so first is most recent
    recent_meal = meals_w_recipe.first()

    if recent_meal is not None:
        date_last_made = recent_meal.scheduled_date.strftime('%d-%b-%Y')
    else:
        date_last_made = 'Never made'

    return date_last_made


def _number_of_times_recipe_made(recipe):
    '''
    Returns the number of times a recipe was made
    '''

    meals_w_recipe = Meal.objects.filter(recipe = recipe).order_by("-scheduled_date")

    # meals sorted by date made (descending), so first is most recent
    count = meals_w_recipe.count()

    return count

def _get_previous_month_and_year(year, month):
    '''
    Returns the previous year and month from the one passed in
    @param year: 4 digit year as string
    @param month: 1 or 2 digit month as string
    @return: tuple of 4 digit year and 1 or 2 digit month
    '''

    year_int = int(year)
    month_int = int(month)

    prev_month = month_int - 1
    if prev_month == 0:
        prev_month = 12
        prev_year = year_int -1
    else:
        prev_year = year_int

    return (prev_year, prev_month)


def _get_next_month_and_year(year: int, month: int):
    '''
    Returns the next year and month from the one passed in
    @param year: 4 digit year
    @param month: 1 or 2 digit month
    @return: tuple of 4 digit year and 1 or 2 digit month
    '''

    year_int = int(year)
    month_int = int(month)

    next_month = month_int + 1
    if next_month == 13:
        next_month = 1
        next_year = year_int + 1
    else:
        next_year = year_int

    return (next_year, next_month)
