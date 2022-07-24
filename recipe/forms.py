from django import forms
from .models import Recipe, RecipeType


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

        return name
