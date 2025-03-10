'''
Name: forms.py
Description: Defines forms for Meal objects
'''

from django import forms
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.template import loader

from . import models


class RecipeWidget(forms.widgets.Select):
    '''
    Class to define custom Recipe Widget
    '''
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
        '''
        Returns the recipe's name
        '''
        return self._recipe_name

    @recipe_name.setter
    def recipe_name(self, value):
        '''
        Sets the recipe's name
        '''
        self._recipe_name = value

    @cached_property
    def media(self):
        '''
        Sets up CSS file imports
        Based on example found here: https://tinyurl.com/pn7ytmpx
        '''
        widget_media = super().media
        # Not sure if js argument does anything as including table.js as part of meals/details.html
        # appears to actually provide access to javascript
        return forms.Media(
            js=widget_media._js + ["home/scripts/table.js"],
            css={"all": ("home/content/site.css",)},
        ) # D:\meal_planner\home\static\home\content\site.css
    

class MealForm(forms.ModelForm):
    '''
    Class to define form for Meal
    '''
    recipe_name = ""

    class Meta:
        '''
        Metadata class
        '''
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


class PrintForm(forms.Form):

    print_choices = [
        ('ALL', 'Print all weeks'), 
        ('SELECT', 'Print only following weeks:')
    ]
    week_choices = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ]

    meal_year = forms.IntegerField(widget=forms.HiddenInput())
    meal_month = forms.IntegerField(widget=forms.HiddenInput())
    print_weeks = forms.ChoiceField(
        choices=print_choices,
        widget = forms.RadioSelect(attrs={'onchange': 'radio_change(this.id, this.value);'}),
        initial='ALL'
    )
    weeks = forms.MultipleChoiceField(
        choices=week_choices
    )
    print_only_meals = forms.BooleanField(
        label='Print only meals',
        initial=False,
        required=False
    )
    print_notes = forms.BooleanField(
        label='Print meal notes',
        initial=True,
        required=False
    )
