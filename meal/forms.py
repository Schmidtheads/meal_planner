from django import forms
from . import models
from django.template import loader
from django.utils.safestring import mark_safe

class RecipeWidget(forms.widgets.Select):
    template_name =  'meal/recipe_select.html'
    _recipe_name = ""

    def get_context(self, name, value, attrs=None, renderer=None):
        return {'widget': {
            'name': name,
            'value': value,
            'recipe_name': self.recipe_name,
        }}

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

    @property
    def recipe_name(self):
        return self._recipe_name

    @recipe_name.setter
    def recipe_name(self, value):
        self._recipe_name = value


class MealForm(forms.ModelForm):

    recipe_name = ""

    class Meta:
        model = models.Meal
        fields = '__all__'
        widgets={'recipe': RecipeWidget()}


    def __init__(self, *args, **kwargs):
        super(MealForm, self).__init__(*args, **kwargs)
        the_meal = kwargs.get('instance')
        
        # Set properties, if a meal for the date was found
        if not the_meal is None:
            self.recipe_name = the_meal.recipe.name
            self.fields['recipe'].widget.recipe_name = self.recipe_name
        

