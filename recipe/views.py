'''
Name:           views.py
Description:    Web Request Handler for Recipe object
Date:           
Author:         M. Schmidt
'''

from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import Recipe, Diner, RecipeRating
from .forms import RatingForm, RecipeForm, RecipeTypeForm, DinerForm


# Create your views here.

def detail(request, id):
    '''
    View to edit or view a Recipe
    '''
    recipe = get_object_or_404(Recipe, pk=id)

    current_user = request.user
    if request.method == "POST": #MIGHT NOT BE NEEDED: and current_user.has_perm('recipe.change_recipe'):
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect("recipes")
    else:
        if current_user.has_perm('recipe.change_recipe'):
            form = RecipeForm(instance=recipe)
        else:
            form = RecipeForm(instance=recipe, readonly_form=True)

    #recipe_rating = calculate_recipe_rating(id)

    return render(request, "recipe/detail.html",
        {
            "form": form,
            "recipe_id": id,
            "recipe_rating": recipe.rating,
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
            "button_label": "Update"
        })


@permission_required('recipe.add_recipe')
def new(request):
    '''
    View used to create a new Recipe
    '''
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("recipes")
    else:
        form = RecipeForm()

    return render(request, "recipe/detail.html", 
                 {"title": "New Recipe",
                  "recipe_id": 0,
                  "recipe_rating": 0,
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "form": form,
                  "button_label": "Create"})


def diner_detail(request):
    '''
    View to edit or view a Diner
    '''
    diner = get_object_or_404(Diner, pk=id)

    if request.method == "POST":
        form = DinerForm(request.POST, instance=diner)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = DinerForm(instance=diner)

    return render(request, "recipe/diner_detail.html",
                 {"form": form,
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "button_label": "Update"})


@permission_required('recipe.rating.add_rating')
def rating_detail(request, id):
    '''
    View to edit or view a recipe rating
    '''
    rating = get_object_or_404(RecipeRating, pk=id)

    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = RatingForm(instance=rating)


    return render(request, "recipe/rating_detail.html",
                 {"form": form,
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "button_label": "Update"})


def ratings_list(request, recipe_id):
    '''
    View to see all the ratings for a recipe
    '''
    recipe = Recipe.objects.get(id=recipe_id)
    recipe_ratings = recipe.reciperating_set.all()

    #recipe_rating = calculate_recipe_rating(recipe_id)

    return render(request, "recipe/rating_list.html",
                  {"recipe_ratings": recipe_ratings,
                   "recipe_rating": recipe.rating,
                   "recipe_name": recipe.name,
                   "recipe_id": recipe_id,
                   "table_name": "Recipe Ratings",
                   "year": datetime.now().year,
                   "company": "Schmidtheads Inc.",})


def recipes(request):
    '''
    View to list all recipes
    '''
    return render(request, "recipe/list.html",
                 {"recipes": Recipe.objects.all(),
                  "table_name": "recipes",
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",})


def new_rating(request, recipe_id):
    '''
    View to create a new recipe rating
    '''
    recipe = Recipe.objects.get(id=recipe_id)
    recipe_name = recipe.name
    current_user = request.user

    if request.method == "POST":
        # Check if rating already exists for user and recipe
        d_matches = Diner.objects.filter(user_name=current_user.username)
        rating_id = -1  # initialize, may be updated below
        rating = None   # intialize, may be updated below
        user_id = -1 if d_matches.count() == 0 else d_matches[0].id
        if user_id != -1:
            r_matches = RecipeRating.objects.filter(
                diner=user_id,
                recipe=recipe_id
            )
            if r_matches.count() != 0:
                rating_id = r_matches[0].id
                rating = RecipeRating.objects.get(id=rating_id)

        # set up form, depending if creating new rating or updating existing one        
        if user_id == -1 or rating_id == -1:
            form = RatingForm(data=request.POST, files=request.FILES)
        else:
            form = RatingForm(data=request.POST, instance=rating)

        if form.is_valid():
            form.save()
            # Go back to the associated recipe
            #TODO: If rating update initiated from rating list, then maybe return there instead of recipe
            return redirect('recipe_detail', recipe_id)
        else:
            # if from is invalid on submission, need to set recipe again
            form.fields['recipe'].initial = recipe         
    else:
        # Steps
        # 1. Check if current user is in Diner table
        d_matches = Diner.objects.filter(user_name=current_user.username)

        #  If user does not exist, insert username, first and last name in table; get row ID
        if d_matches.count() == 0:
            new_user = Diner.objects.create(
                user_name = current_user.username,
                first_name = current_user.first_name,
                last_name = current_user.last_name
            )
            user_id = new_user.id
        else:
            # If user does exist, get row ID
            # If multiple instances of the same user exist (it shouldn't!),
            # use the first instance
            user_id = d_matches[0].id

        # 2. Check if rating for current user and recipe already exists
        r_matches = RecipeRating.objects.filter(recipe=recipe_id, diner=user_id)

        # If it does get the recipe rating row and get recipe rating
        if r_matches.count() == 1:
            rating_id = r_matches[0].id
            rating_value = r_matches[0].rating
        else:
            rating_value = 1

        # 3. Open form, pasinging in row ID or just rating?

        if current_user.has_perm('recipe.add_reciperating') or current_user.has_perm('recipe.update_reciperating'):
            form = RatingForm(initial={
                'diner': user_id,
                'recipe': recipe_id,
                'rating': rating_value})

            #TODO: hide diner dropdown unless admin
            diner_field = form.fields['diner']
            diner_field.widget = diner_field.hidden_widget()            
        else:
            # if user does not have permission to add or update rating, then maybe they shouldn't be here at all?
            # perhaps retrict hyperlink for rating on recipe list page so it is not clickable instead
            form = RatingForm(readonly_form=True)        
        #form.fields['recipe'].initial = recipe

    return render(request, "recipe/rating_detail.html",
                 {
                  "form": form,
                  "title": "New Rating",
                  "recipe_name": recipe_name,
                  "button_label": "Create",
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                 })


# Creating Recipe Types for a Recipe implemented using guidance
# from this page: https://tinyurl.com/4b5yt3rw

def RecipeTypeCreatePopup(request):
    '''
    Creates a popup to create a new recipe type
    '''
    form = RecipeTypeForm(request.POST or None)
    if form.is_valid():
        instance = form.save()

		## Add the new value to "#id_recipe_types". This is the element id in the form

        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_recipe_types", "checkbox");</script>' % (instance.pk, instance))

    return render(request, "recipe/recipe_type.html",
                  {"form": form,
                   "year": datetime.now().year,
                   "company": "Schmidtheads Inc.",
                   "table_name": "recipe_type"})


# Calcule Recipe Rating
def calculate_recipe_rating(recipe_id):
    '''
    Calculate a recipe rating
    '''
    recipe = Recipe.objects.get(id=recipe_id)
    all_ratings = recipe.reciperating_set.all()

    # Calculate average rating
    sum_rating = 0
    for rating in all_ratings:
        sum_rating += rating.rating

    average_rating = 0 if all_ratings.count() == 0 else sum_rating / all_ratings.count()

    return average_rating
