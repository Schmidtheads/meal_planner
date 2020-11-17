from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelform_factory

from .models import Cookbook, Author

CookbookForm = modelform_factory(Cookbook, exclude=[])

def detail(request, id):
    cookbook = get_object_or_404(Cookbook, pk=id)

    if request.method == "POST":
        form = CookbookForm(request.POST, instance=cookbook)
        if form.is_valid():
            form.save()
            return redirect("cookbooks")
    else:
        form = CookbookForm(instance=cookbook)

    return render(request, "cookbook/detail.html",
                 {"form": form})


def cookbooks(request):

    return render(request, "cookbook/list.html",
                  {"cookbooks": Cookbook.objects.all(),
                   "table_name": "cookbooks"})

