'''
Name: models.py
Description: Defines the schema of the Meals model
'''

from django.db import models
from recipe.models import Recipe


class Meal(models.Model):
    '''
    Defines the Meal schema
    '''
    scheduled_date = models.DateField()
    was_made = models.BooleanField(default=False)
    notes = models.TextField(max_length=250, blank=True)  # optional field
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


    def __str__(self):
        fdate = self.scheduled_date.strftime("%Y-%b-%d")  # date format e.g. 2020-Oct-13
        return f"{self.recipe} on {fdate}"

    