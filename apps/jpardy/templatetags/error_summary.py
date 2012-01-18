"""
This module contains a custom template tag called "error_summary" that takes a 
form or formset as its argument and produces an unordered list summarizing all 
of the errors. 

This tag is meant to make it easy to show every error in a form or formset in 
one place, as opposed to showing each field error next to each field.

"""

from django import template
from django import forms
from django.forms import formsets
from django.forms.forms import NON_FIELD_ERRORS

register = template.Library()

@register.inclusion_tag('form_errors.html')
def error_summary(obj):
    error_list = []

    if isinstance(obj, forms.BaseForm):
        for field, errors in obj.errors.items():
            for error in errors:
                error_string = ''
                
                if field != NON_FIELD_ERRORS:
                    error_string = "Field \"%s\" | " % obj.fields[field].label

                error_string += error
                error_list.append(error_string)

    elif isinstance(obj, formsets.BaseFormSet):
        for error in obj.non_form_errors():
            error_list.append(error)

        for index, form in zip(range(0, len(obj.initial_forms)), obj.initial_forms):
            for field, errors in form.errors.items():
                for error in errors:
                    error_string = "Form #%d | " % (index + 1)

                    if field != NON_FIELD_ERRORS:
                        error_string += "Field \"%s\" | " % form.fields[field].label

                    error_string += error
                    error_list.append(error_string)

    return {'error_list': error_list}
