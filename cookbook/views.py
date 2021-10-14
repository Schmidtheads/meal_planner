import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelform_factory
from datetime import datetime

from .models import Cookbook, Author
from .forms import AuthorForm

CookbookForm = modelform_factory(Cookbook, exclude=[])

def detail(request, id):
    cookbook = get_object_or_404(Cookbook, pk=id)

    if request.method == "POST":
        form = CookbookForm(request.POST, request.FILES, instance=cookbook)
        if form.is_valid():
            form.save()
            return redirect("cookbooks")
    else:
        form = CookbookForm(instance=cookbook)

    return render(request, "cookbook/detail.html",
                 {"title": "Meal Planner",
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "form": form,
                  "cookbook": cookbook})


def new(request):
    if request.method == "POST":
        form = CookbookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("cookbooks")
    else:
        form = CookbookForm()

    return render(request, "cookbook/detail.html", 
                 {"title": "Meal Planer",
                  "year": datetime.now().year,
                  "company": "Schmidtheads Inc.",
                  "form": form})


def cookbooks(request):

    return render(request, "cookbook/list.html",
                  {"cookbooks": Cookbook.objects.all(),
                   "year": datetime.now().year,
                   "company": "Schmidtheads Inc.",
                   "table_name": "cookbooks"})


# Editing/Creating authors from a cookbook implemented using guidance
# from this page: https://tinyurl.com/4b5yt3rw

def AuthorCreatePopup(request):
	form = AuthorForm(request.POST or None)
	if form.is_valid():
		instance = form.save()

		## Change the value of the "#id_author". This is the element id in the form

		return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))

	return render(request, "cookbook/author.html",
                  {"form": form,
                   "year": datetime.now().year,
                   "company": "Schmidtheads Inc.",
                   "table_name": "authors"})


def AuthorEditPopup(request, id=None):
	instance = get_object_or_404(Author, pk=id)
	form = AuthorForm(request.POST or None, instance=instance)
	if form.is_valid():
		instance = form.save()

		## Change the value of the "#id_author". This is the element id in the form

		return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))

	return render(request, "cookbook/author.html",
               {"form": form,
                   "year": datetime.now().year,
                   "company": "Schmidtheads Inc.",
                   "table_name": "authors"})
