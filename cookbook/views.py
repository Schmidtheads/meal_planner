'''
Name:           views.py
Description:    Web Request Handler for Cookbook object
Date:           
Author:         M. Schmidt
'''

from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime

from .models import Cookbook, Author
from .forms import AuthorForm, CookbookForm


def detail(request, id):
    cookbook = get_object_or_404(Cookbook, pk=id)

    current_user = request.user
    if request.method == "POST":  # may need to check user permissions
        form = CookbookForm(data=request.POST, files=request.FILES, instance=cookbook)
        if form.is_valid():
            form.save()
            return redirect("cookbooks")
    else:
        if current_user.has_perm('cookbook.change_cookbook'):
            form = CookbookForm(instance=cookbook)
        else:
            form = CookbookForm(instance=cookbook, readonly_form=True)

    return render(request, "cookbook/detail.html",
        {
            "title": "Cookbook",
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
            "form": form,
            "cookbook": cookbook
        })


@permission_required('cookbook.add_cookbook')
def new(request):
    if request.method == "POST":
        form = CookbookForm(data=request.POST, files=request.FILES, readonly_form=False)
        if form.is_valid():
            form.save()
            return redirect("cookbooks")
        
        return render(request, 'cookbook/detail.html', 
            {
                "title": "New Cookbook",
                "year": datetime.now().year,
                "company": "Schmidtheads Inc.",
                "form": form
            }) 
    else:
        form = CookbookForm()

    return render(request, "cookbook/detail.html", 
        {
            "title": "New Cookbook",
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
            "form": form
        })


def cookbooks(request):

    return render(request, "cookbook/list.html",
                  {"title": "Cookbooks",
                   "cookbooks": Cookbook.objects.all(),
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
