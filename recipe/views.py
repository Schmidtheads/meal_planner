from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelform_factory
from datetime import datetime

from .models import Recipe, RecipeType
from .forms import RecipeForm, RecipeTypeForm


# Create your views here.

def detail(request, id):
    recipe = get_object_or_404(Recipe, pk=id)

    if request.method == "POST":
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = RecipeForm(instance=recipe)

    return render(request, "recipe/detail.html",
                 {"form": form,
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
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "form": form,
                  "button_label": "Create"})


def recipes(request):

    return render(request, "recipe/list.html",
                 {"recipes": Recipe.objects.all(),
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "table_name": "recipes"})


# Creating Recipe Types for a Recipe implemented using guidance
# from this page: https://tinyurl.com/4b5yt3rw

def RecipeTypeCreatePopup(request):
	form = RecipeTypeForm(request.POST or None)
	if form.is_valid():
		instance = form.save()

		## Change the value of the "#id_recipe_types". This is the element id in the form

		return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_recipe_types");</script>' % (instance.pk, instance))

	return render(request, "recipe/recipe_type.html",
                  {"form": form,
                   "year": datetime.now().year,
                   "company": "Schmidtheads Inc.",
                   "table_name": "recipe_type"})


