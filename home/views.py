"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'home/index.html',
        {
            'title':'Meal Planner',
            'year': datetime.now().year,
            'company': 'Schmidtheads',
            'application': 'Meal Planner',
        }
    )


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'home/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'company': 'Schmidtheads',            
            'year':datetime.now().year,
        }
    )


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'home/about.html',
        {
            'title':'About Meal Planner',
            'message':'Overview of the Meal Planner application.',
            'company': 'Schmidtheads',
            'year':datetime.now().year,
        }
    )


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'home/signup.html', {'form': form})
   