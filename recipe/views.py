from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelform_factory
from datetime import datetime

from .models import Recipe, Diner, RecipeRating
from .forms import RatingForm, RecipeForm, RecipeTypeForm, DinerForm


# Create your views here.

def detail(request, id):
    recipe = get_object_or_404(Recipe, pk=id)

    if request.method == "POST":
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect("recipes")
    else:
        form = RecipeForm(instance=recipe)

    recipe_rating = calculate_recipe_rating(id)

    return render(request, "recipe/detail.html",
                 {"form": form,
                 "recipe_id": id,
                 "recipe_rating": recipe_rating,
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "button_label": "Update"})


def new(request):
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


def rating_detail(request, id):
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
    recipe = Recipe.objects.get(id=recipe_id)
    recipe_ratings = recipe.reciperating_set.all()

    recipe_rating = calculate_recipe_rating(recipe_id)

    return render(request, "recipe/rating_list.html",
                  {"recipe_ratings": recipe_ratings,
                   "recipe_rating": recipe_rating,
                   "recipe_name": recipe.name,
                   "recipe_id": recipe_id,
                   "table_name": "Recipe Ratings",
                   "year": datetime.now().year,
                   "company": "Schmidtheads Inc.",})


def recipes(request):

    return render(request, "recipe/list.html",
                 {"recipes": Recipe.objects.all(),
                  "table_name": "recipes",
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",})


def new_rating(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    recipe_name = recipe.name

    if request.method == "POST":
        form = RatingForm(request.POST, request.FILES)

        #TODO: ensure a diner can't have more than one rating per recipe
        if form.is_valid():
            form.save()
            # Go back to the associated recipe
            return redirect('recipe_detail', recipe_id)
        else:
            # if from is invalid on submission, need to set recipe again
            form.fields['recipe'].initial = recipe         
    else:
        form = RatingForm()
        # Set recipe to read only
        form.fields['recipe'].initial = recipe

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
    recipe = Recipe.objects.get(id=recipe_id)
    all_ratings = recipe.reciperating_set.all()

    # Calculate average rating
    sum_rating = 0
    for rating in all_ratings:
        sum_rating += rating.rating

    average_rating = 0 if all_ratings.count() == 0 else sum_rating / all_ratings.count()

    return average_rating
