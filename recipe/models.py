from django.db import models
from cookbook.models import Cookbook

# Create your models here.

class Recipe(models.Model):
    name = models.CharField(max_length=50)
    cook_book = models.ForeignKey(Cookbook, on_delete=models.CASCADE)
    page_number = models.PositiveSmallIntegerField()
    notes = models.CharField(max_length=750)

    def __str__(self):
        return f"{self.name} {self.cook_book}"


class RecipeType(models.Model):
    name = models.CharField(max_length=20)
    recipes = models.ManyToManyField(Recipe)

    def __str__(self):
        return f"{self.name}"
