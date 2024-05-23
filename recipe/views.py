'''
Name:           views.py
Description:    Web Request Handler for Recipe object
Date:           
Author:         M. Schmidt
'''

from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import Recipe, Diner, RecipeRating
from .forms import RatingForm, RecipeForm, RecipeTypeForm, DinerForm


def detail(request, id):
    '''
    View to edit or view a Recipe
    '''
    '''
    View to edit or view a Recipe
    '''
    recipe = get_object_or_404(Recipe, pk=id)

    current_user = request.user
    if request.method == "POST": #MIGHT NOT BE NEEDED: and current_user.has_perm('recipe.change_recipe'):
        form = RecipeForm(data=request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect("recipes")
    else:
        if current_user.has_perm('recipe.change_recipe'):
            form = RecipeForm(instance=recipe)
        else:
            form = RecipeForm(instance=recipe, readonly_form=True)

    return render(request, "recipe/detail.html",
        {
            "form": form,
            "recipe_id": id,
            "recipe_rating": recipe.rating_as_string,
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
            "button_label": "Update"
        }
    )


@permission_required('recipe.add_recipe')
def new(request):
    '''
    View used to create a new Recipe
    '''
    '''
    View used to create a new Recipe
    '''
    if request.method == "POST":
        form = RecipeForm(data=request.POST, files=request.FILES, readonly_form=False)
        if form.is_valid():
            form.save()
            return redirect("recipes")
    else:
        form = RecipeForm()

    return render(request, "recipe/detail.html", 
        {
            "title": "New Recipe",
            "recipe_id": 0,
            "recipe_rating": "-",
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
            "form": form,
            "button_label": "Create"
        }
    )


def diner_detail(request):
    '''
    View to edit or view a Diner
    '''
    '''
    View to edit or view a Diner
    '''
    diner = get_object_or_404(Diner, pk=id)

    if request.method == "POST":
        form = DinerForm(request.POST, instance=diner)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = DinerForm(instance=diner)

    return render(request, "recipe/diner_detail.html",
        {
            "form": form,
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
            "button_label": "Update"
        }
    )


def ratings_list(request, recipe_id):
    '''
    View to see all the ratings for a recipe
    '''
    '''
    View to see all the ratings for a recipe
    '''
    recipe = Recipe.objects.get(id=recipe_id)
    recipe_ratings = recipe.reciperating_set.all()  #type: ignore

    # check if current user has a rating to update
    # if not, flag, so "New" button can be enabled.
    current_user = request.user
    diner_id = get_user_diner(current_user)
    diner_has_rating = recipe_ratings.filter(diner=diner_id).count() != 0

    return render(request, "recipe/rating_list.html",
        {
            "recipe_ratings": recipe_ratings,
            "recipe_rating": recipe.rating_as_string,
            "recipe_name": recipe.name,
            "recipe_id": recipe_id,
            "diner_has_rating": diner_has_rating,
            "table_name": "Recipe Ratings",
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
        }
    )


def recipes(request):
    '''
    View to list all recipes
    '''
    '''
    View to list all recipes
    '''
    return render(request, "recipe/list.html",
        {
            "recipes": Recipe.objects.all(),
            "table_name": "recipes",
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
        }
    )


@permission_required('recipe.add_reciperating')
def update_rating_from_list(request, recipe_id: int):
    '''
    View to update recipe rating, launched from recipe list
    '''

    return update_rating(request, recipe_id, 
        'recipes', 
        'Back to Recipe List',
        'recipes'
    )


@permission_required('recipe.add_reciperating')
def update_rating_from_recipe(request, recipe_id: int):
    '''
    View to update recipe rating, launched from recipe
    '''

    return update_rating(request, recipe_id, 
        'recipe_rating_list', 
        'Back to Ratings List',
        'recipe_rating_list'
    )


def update_rating(request, recipe_id: int, 
    redirect_page: str, 
    exit_label: str,
    redirect_path: str):
    '''
    View to create a new recipe rating
    THIS VIEW SHOULD NOT BE CALLED DIRECTLY FROM TEMPLATE

    @param request: request object
    @param recipe_id: id of recipe to rate
    @param redirect_page: name of page to redirect back to
    @param exit_label: label for exit button
    '''
    recipe = Recipe.objects.get(id=recipe_id)
    recipe_name = recipe.name
    current_user = request.user
    button_label = "Update"  # default value

    if request.method == "POST":
        rating_id = -1  # initialize, may be updated below
        rating = None   # intialize, may be updated below        

        # if super user, check rating based on passed in Diner
        if current_user.is_superuser:
            user_id = int(request.POST.get('diner', '-1'))
        else:
        # Use currently logged in user for rating check

            # Check if rating already exists for user and recipe
            d_matches = Diner.objects.filter(user_name=current_user.username)
            user_id = -1 if d_matches.count() == 0 else d_matches[0].id  #type: ignore
        
        if user_id != -1:
            r_matches = RecipeRating.objects.filter(
                diner=user_id,
                recipe=recipe_id
            )
            if r_matches.count() != 0:
                rating_id = r_matches[0].id  #type: ignore
                rating = RecipeRating.objects.get(id=rating_id)

        # set up form, depending if creating new rating or updating existing one        
        if user_id == -1 or rating_id == -1:
            form = RatingForm(data=request.POST, files=request.FILES)
        else:
            form = RatingForm(data=request.POST, instance=rating)

        if form.is_valid():
            form.save()
            # Go back to the originating page
            # if redirecting back to ratings list, need to specify recipe id
            if redirect_page == 'recipe_rating_list':
                return redirect(redirect_page, recipe_id)
            else:
                return redirect(redirect_page)
        else:
            # if from is invalid on submission, need to set recipe again
            form.fields['recipe'].initial = recipe         
    else:
        # Steps
        # 1. Check if current user is in Diner table
        user_id = get_user_diner(current_user)

        # 2. Check if rating for current user and recipe already exists
        if user_id != -1:  # only find ratings for non-anymous users
            r_matches = RecipeRating.objects.filter(recipe=recipe_id, diner=user_id)
 
            # If it does get the recipe rating row and get recipe rating
            # Also set button label to "Update" or "Create" appropriately
            if r_matches.count() == 1:
                rating_id = r_matches[0].id  #type: ignore
                rating_value = r_matches[0].rating
                button_label = "Update"
            else:
                rating_value = 1
                button_label = "Create"
        else:
            # for anonymous user, will be prompted to login
            # so button lable and intial rating value are moot
            # but set here for consistency
            button_label = ''
            rating_value = 0

        # 3. Open form, pasinging in row ID or just rating?

        if current_user.has_perm('recipe.add_reciperating') or current_user.has_perm('recipe.update_reciperating'):
            form = RatingForm(initial={
                'diner': user_id,
                'recipe': recipe_id,
                'rating': rating_value})

            # hide diner field, unless user is admin
            diner_field = form.fields['diner']
            if not current_user.is_superuser:
                diner_field.widget = diner_field.hidden_widget()            
        else:
            # if user does not have permission to add or update rating, 
            # then maybe they shouldn't be here at all?
            # perhaps restrict hyperlink for rating on recipe list page
            # so it is not clickable instead
            form = RatingForm(readonly_form=True)        


    return render(request, "recipe/rating_detail.html",
        {
            "form": form,
            "title": "Update Rating",
            "recipe_name": recipe_name,
            "recipe_id": recipe_id,
            "redirect_page": redirect_path,
            "button_label": button_label,
            "button_exit_label": exit_label,
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
        }
    )


# Creating Recipe Types for a Recipe implemented using guidance
# from this page: https://tinyurl.com/4b5yt3rw

def RecipeTypeCreatePopup(request):
    '''
    Creates a popup to create a new recipe type
    '''
    form = RecipeTypeForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
    '''
    Creates a popup to create a new recipe type
    '''
    form = RecipeTypeForm(request.POST or None)
    if form.is_valid():
        instance = form.save()

		## Add the new value to "#id_recipe_types". This is the element id in the form

        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_recipe_types", "checkbox");</script>' % (instance.pk, instance))
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_recipe_types", "checkbox");</script>' % (instance.pk, instance))

    return render(request, "recipe/recipe_type.html",
        {
            "form": form,
            "year": datetime.now().year,
            "company": "Schmidtheads Inc.",
            "table_name": "recipe_type"
        }
    )


# Calcule Recipe Rating
def calculate_recipe_rating(recipe_id):
    '''
    Calculate a recipe rating
    '''
    '''
    Calculate a recipe rating
    '''
    recipe = Recipe.objects.get(id=recipe_id)
    all_ratings = recipe.reciperating_set.all()  #type: ignore

    # Calculate average rating
    sum_rating = 0
    for rating in all_ratings:
        sum_rating += rating.rating

    average_rating = 0 if all_ratings.count() == 0 else sum_rating / all_ratings.count()

    return average_rating


def get_user_diner(user) -> int:
    '''
    Checks if passed in user is in Diner table
    If not, they are added. Return id of diner

    @params user: user object
    @return: id of Diner for current user
    '''

    # if user is anonymous (i.e. nobody logged in)
    # return user_id of -1
    if user.is_anonymous:
        return -1

    # Check if current user is in Diner table
    d_matches = Diner.objects.filter(user_name=user.username)

    # If user does not exist, insert username, first and last name in table; get row ID
    if d_matches.count() == 0:
        new_user = Diner.objects.create(
            user_name = user.username,
            first_name = user.first_name,
            last_name = user.last_name
        )
        user_id = new_user.id  #type: ignore
    else:
        # If user does exist, get row ID
        # If multiple instances of the same user exist (it shouldn't!),
        # use the first instance
        user_id = d_matches[0].id  #type: ignore

    return user_id
