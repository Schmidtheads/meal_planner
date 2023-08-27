"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest

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
