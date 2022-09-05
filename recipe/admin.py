from django.contrib import admin

from .models import Recipe, RecipeType, RecipeRating, Diner

# Register your models here (format as class names)

admin.site.register(Recipe)
admin.site.register(RecipeType)
admin.site.register(RecipeRating)
admin.site.register(Diner)