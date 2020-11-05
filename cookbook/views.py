from django.shortcuts import render, get_object_or_404, redirect

from .models import Cookbook, Author

def detail(request, id):
    cookbook = get_object_or_404(Cookbook, pk=id)
    return render(request, "cookbook/detail.html", {"cookbook": cookbook})


def cookbooks(request):
    return render(request, "cookbook/list.html",
                  {"cookbooks": Cookbook.objects.all()})

