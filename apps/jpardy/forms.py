from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.forms import ModelForm

from apps.jpardy.models import *
from django.contrib.auth.models import User


class BaseCategoryFormSet(BaseInlineFormSet):
    """Base formset for category editing."""

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


# Formset for category editing.
CategoryFormSet = inlineformset_factory(
                    Category, 
                    Question, 
                    extra=0, 
                    can_delete=False, 
                    formset=BaseCategoryFormSet)


class CategoryNameForm(ModelForm):
    """Simple form for specifying a category's name."""

    class Meta:
        model = Category
        fields = ('name',)


class FinalQuestionForm(ModelForm):

    class Meta:
        model = FinalQuestion
        fields = ('category', 'question', 'answer',)


class InitialGamePrepForm(forms.Form):
    """Form that handles player and category selection for a new game."""

    def __init__(self, *args, **kwargs):
        category_qs = kwargs.pop('category_qs', Category.objects.all())
        fq_qs = kwargs.pop('fq_qs', FinalQuestion.objects.all())
        super(InitialGamePrepForm, self).__init__(*args, **kwargs)
        self.fields['categories'] = forms.ModelMultipleChoiceField(
                                            queryset=category_qs,
                                            label='Categories')
        self.fields['final_question'] = forms.ModelChoiceField(
                                            queryset=fq_qs,
                                            label='Final Question')

    players = forms.ModelMultipleChoiceField(
                                            queryset=User.objects.all(), 
                                            label='Players')


# Daily double selection formset for each category in a game.
CategoryInGameDailyDoubleFormSet = inlineformset_factory(
                                        CategoryInGame,
                                        QuestionInGame,
                                        extra=0,
                                        can_delete=False,
                                        fields=('daily_double',))


class BaseGameDailyDoubleFormSet(BaseInlineFormSet):
    """
    Base formset for daily double selection for a game.

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


# Daily double selection formset for a whole game.
GameDailyDoubleFormSet = inlineformset_factory(
                                        Game,
                                        CategoryInGame,
                                        extra=0,
                                        can_delete=False,
                                        fields=[],
                                        formset=BaseGameDailyDoubleFormSet)
