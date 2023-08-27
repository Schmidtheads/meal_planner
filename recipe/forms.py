from django import forms
from .models import Recipe, RecipeRating, RecipeType, Diner
import string


class RecipeForm(forms.ModelForm):
    recipe_types = forms.ModelMultipleChoiceField(
        queryset=RecipeType.objects.all(), 
        required=False, 
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Recipe
        fields = '__all__'
        

class RecipeTypeForm(forms.ModelForm):
    class Meta:
        model = RecipeType
        fields = '__all__'

    def clean_name(self):
        name = self.cleaned_data.get('name')

        for instance in RecipeType.objects.all():
            if str(instance.name).lower() == str(name).lower():
                raise forms.ValidationError(f'There is already a Recipe Tag of "{name}"')

        # Format recipe type to capital case
        return string.capwords(str(name))


class DinerForm(forms.ModelForm):
    class Meta:
        model = Diner
        fields = '__all__'


class RatingForm(forms.ModelForm):
    class Meta:
        model = RecipeRating
        fields = '__all__'


    def clean_rating(self):
        rating = self.cleaned_data.get('rating')   

        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating value must be between 1 and 5')

        return rating


    def clean_diner(self):
        # check to make sure that only one diner has rating for current recipe
        recipe = self.cleaned_data.get('recipe')
        diner = self.cleaned_data.get('diner')
        recipe_ratings = RecipeRating.objects.filter(recipe = recipe).filter(diner = diner)
        
        if recipe_ratings.count() > 0:
            raise forms.ValidationError('Diner has already rated this recipe')

        return diner
