from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms import ModelForm

from apps.jpardy.models import Category

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

class SelectCategoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', Category.objects.all())
        super(SelectCategoryForm, self).__init__(*args, **kwargs)
        self.fields['categories'] = forms.ModelMultipleChoiceField(
                                            queryset=queryset,
                                            label='Categories')
