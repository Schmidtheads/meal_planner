from django.db import models
from cookbook.models import Cookbook

# Create your models here.


class RecipeType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    name = models.CharField(max_length=50)
    cook_book = models.ForeignKey(Cookbook, on_delete=models.CASCADE)
    page_number = models.PositiveSmallIntegerField()
    notes = models.CharField(max_length=750)
    recipe_types = models.ManyToManyField(RecipeType)

    def __str__(self):
        return f"{self.name} {self.cook_book}"


class Diner(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)


    def last_name_first(self):
        return f"{self.last_name}, {self.first_name}"


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class RecipeRating(models.Model):
    rating = models.PositiveSmallIntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    diner = models.ForeignKey(Diner, on_delete=models.CASCADE)