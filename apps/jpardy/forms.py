from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.forms import ModelForm

from apps.jpardy.models import *
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

CategoryInGameDailyDoubleFormSet = inlineformset_factory(
                                        CategoryInGame,
                                        QuestionInGame,
                                        extra=0,
                                        can_delete=False,
                                        fields=('daily_double',))


class BaseGameDailyDoubleFormSet(BaseInlineFormSet):
    """
    Nested formset code from:
    http://yergler.net/blog/2009/09/27/nested-formsets-with-django/.

    The big 1.3 change to this code is

        CategoryInGameDailyDoubleFormSet(data=self.data or None,
        
    where we had to add "or None".
    """

    def add_fields(self, form, index):
        # allow the super class to create the fields as usual
        super(BaseGameDailyDoubleFormSet, self).add_fields(form, index)
 
        # created the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance=None
            pk_value = hash(form.prefix)
 
        # store the formset in the .nested property
        form.nested = [
            CategoryInGameDailyDoubleFormSet(data=self.data or None,
                                             instance = instance,
                                             prefix = 'CATEGORIES_%s' % pk_value)]

    def is_valid(self):
        result = super(BaseGameDailyDoubleFormSet, self).is_valid()
 
        for form in self.forms:
            if hasattr(form, 'nested'):
                for n in form.nested:
                    # make sure each nested formset is valid as well
                    result = result and n.is_valid()
 
        return result

    def clean(self):
        if any(self.errors):
            return

        form_values = zip(*self.data.items())[1]

        if form_values.count(u'on') > 2:
            raise forms.ValidationError("Only two daily doubles are allowed.")

    def save_all(self, commit=True):
        """Save all formsets and along with their nested formsets."""
 
        # Save without committing (so self.saved_forms is populated)
        # -- We need self.saved_forms so we can go back and access
        #    the nested formsets
        objects = self.save(commit=False)
 
        # Save each instance if commit=True
        if commit:
            for o in objects:
                o.save()
 
        # save many to many fields if needed
        if not commit:
            self.save_m2m()
 
        # save the nested formsets
        for form in set(self.initial_forms + self.saved_forms):
            for nested in form.nested:
                nested.save(commit=commit)

GameDailyDoubleFormSet = inlineformset_factory(
                                        Game,
                                        CategoryInGame,
                                        extra=0,
                                        can_delete=False,
                                        fields=[],
                                        formset=BaseGameDailyDoubleFormSet)
