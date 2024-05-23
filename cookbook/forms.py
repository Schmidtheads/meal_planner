from django import forms
from .models import Author, Cookbook


class CookbookForm(forms.ModelForm):
    class Meta:
        model = Cookbook
        fields = '__all__'

    def __init__(self, readonly_form=False, *args, **kwargs):
        super(CookbookForm, self).__init__(*args, **kwargs)
        if readonly_form:
            for field in self.fields:
                self.fields[field].disabled = True


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'
