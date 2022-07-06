from django import forms
from .models import RecipeType


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
