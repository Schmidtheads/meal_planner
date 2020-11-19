from django.contrib import admin

from .models import Recipe, RecipeType

# Register your models here (format as class names)

admin.site.register(Recipe)
admin.site.register(RecipeType)
