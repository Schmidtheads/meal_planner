from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelform_factory

from .models import Recipe, RecipeType

RecipeForm = modelform_factory(Recipe, exclude=[])

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
                 {"form": form})