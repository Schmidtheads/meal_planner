'''
Name: models.py
Description: Defines the schema and behaviour for Recipe model
'''

from django.db import models
from cookbook.models import Cookbook


# Create your models here.

class RecipeType(models.Model):
    '''
    Defines the RecipeType schema
    '''
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"


    class Meta:
        '''
        Metadata of the RecipeType
        '''
        # Order the output by the Recipe Type name
        ordering = ['name']


class Recipe(models.Model):
    '''
    Defines the Recipe schema
    '''
    name = models.CharField(max_length=50)
    cook_book = models.ForeignKey(Cookbook, on_delete=models.CASCADE, blank=True, null=True)
    page_number = models.PositiveSmallIntegerField()
    notes = models.CharField(max_length=750, blank=True)
    recipe_types = models.ManyToManyField(RecipeType)

    def rating(self):
        '''
        Calculate a recipe rating
        '''
        recipe = Recipe.objects.get(id=self.id)
        all_ratings = recipe.reciperating_set.all()

        # Calculate average rating
        sum_rating = 0
        for rating in all_ratings:
            sum_rating += rating.rating

        average_rating = 0 if all_ratings.count() == 0 else sum_rating / all_ratings.count()

        return average_rating


    def __str__(self):
        return f"{self.name} {self.cook_book}"


class Diner(models.Model):
    '''
    Defines the Diner schema
    '''
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)


    def last_name_first(self):
        '''
        Returns the Diner's name, last name first
        '''
        return f"{self.last_name}, {self.first_name}"


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class RecipeRating(models.Model):
    '''
    Defines the ReciepRating schema
    '''
    rating = models.PositiveSmallIntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    diner = models.ForeignKey(Diner, on_delete=models.CASCADE)
