from django.db import models
from recipe.models import Recipe

import datetime


class Meal(models.Model):
    scheduled_date = models.DateField()
    was_made = models.BooleanField()
    note = models.CharField(max_length=250)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


    def __str__(self):
        fdate = self.scheduled_date.strftime("%Y-%b-%d")  # date format e.g. 2020-Oct-13
        return f"{self.recipe} on {fdate}"