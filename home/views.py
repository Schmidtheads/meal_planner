"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group

from .forms import SignUpForm

DEFAULT_USER_GROUP = 'Diner'

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
            'message':'Need help? Questions? Suggestions? Need somewhere to send a postcard?',
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
    '''
    Signing up a new user from this post
    https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
    '''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()

            # Automatically log user in
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            # Add user to default group
            #default_group = Group.objects.get(name=DEFAULT_USER_GROUP) 
            
            default_group = Group.objects.filter(name=DEFAULT_USER_GROUP).first()
            if default_group: 
                default_group.user_set.add(user)  # type: ignore
            else:
                print(f'User group {DEFAULT_USER_GROUP} not found')
            
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 
        'home/signup.html', 
        {
            'year': datetime.now().year,
            'company': 'Schmidtheads Inc.',
            'form': form
        }
    )
   