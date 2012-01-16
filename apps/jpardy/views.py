from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.http import HttpResponse

from apps.jpardy.models import *
from apps.jpardy.forms import BaseCategoryFormSet
from django.forms.models import inlineformset_factory

@login_required
def home(request):
    return render_to_response('home.html',
                              context_instance=RequestContext(request))

@login_required
def edit(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.user != category.user:
        return HttpResponse("You do not own this category.")

    CategoryFormSet = inlineformset_factory(
                        Category, 
                        Question, 
                        extra=0, 
                        can_delete=False, 
                        exclude=('daily_double',), 
                        formset=BaseCategoryFormSet)

    if request.method == 'POST':
        formset = CategoryFormSet(request.POST, instance=category)
        if formset.is_valid():
            formset.save()
    else:
        formset = CategoryFormSet(instance=category)

    return render_to_response(
                        "edit.html", 
                        {"formset": formset,
                         "category": category,}, 
                         context_instance=RequestContext(request))
