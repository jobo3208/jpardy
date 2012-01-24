from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms import ModelForm

from apps.jpardy.models import Category
from django.contrib.auth.models import User

class BaseCategoryFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        values = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            value = form.cleaned_data['value']
            if value in values:
                raise forms.ValidationError("Each question must have a unique money value.")
            values.append(value)

class CategoryNameForm(ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

class InitialGamePrepForm(forms.Form):
    def __init__(self, *args, **kwargs):
        category_qs = kwargs.pop('category_qs', Category.objects.all())
        super(InitialGamePrepForm, self).__init__(*args, **kwargs)
        self.fields['categories'] = forms.ModelMultipleChoiceField(
                                            queryset=category_qs,
                                            label='Categories')

    players = forms.ModelMultipleChoiceField(
                                            queryset=User.objects.all(), 
                                            label='Players')
