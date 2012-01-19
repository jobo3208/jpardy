from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.http import HttpResponse

from apps.jpardy.models import *
from apps.jpardy.forms import *
from django.forms.models import inlineformset_factory

@login_required
def home(request):
    return render_to_response('home.html',
                              context_instance=RequestContext(request))

@login_required
def manage(request):
    if request.method == 'POST':
        category_form = CategoryNameForm(request.POST)
        if category_form.is_valid():
            new_category = category_form.save(commit=False)
            new_category.user = request.user
            new_category.save()

            # Give a blank form if we succeeded.
            category_form = CategoryNameForm()
    else:
        category_form = CategoryNameForm()

    categories = Category.objects.filter(user=request.user)

    return render_to_response('manage.html',
                              {'categories': categories,
                               'category_form': category_form,},
                              context_instance=RequestContext(request))

@login_required
def edit(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.user != category.user:
        return error(request, "You do not own this category.")

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
            return redirect('/manage/')
    else:
        formset = CategoryFormSet(instance=category)

    return render_to_response(
                        "edit.html", 
                        {"formset": formset,
                         "category": category,}, 
                         context_instance=RequestContext(request))

@login_required
def delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.user != category.user:
        return error(request, "You do not own this category.")

    if request.method == 'POST':
        category.delete()
        return redirect('/manage/')

    return render_to_response(
                        "confirm_delete.html", 
                        {"category": category,}, 
                        context_instance=RequestContext(request))

@login_required
def play(request):
    if request.method == 'POST':
        form = SelectCategoryForm(request.POST)
        if form.is_valid():
            ret = ''
            for k, v in form.cleaned_data.items():
                for a in v:
                    ret += unicode(a) + '\n'

            return HttpResponse(ret)
    else:
        category_choices = Category.objects.filter(user=request.user)
        form = SelectCategoryForm(queryset=category_choices)

    return render_to_response(
                        "select_categories.html",
                        {"form": form},
                        context_instance=RequestContext(request))

def error(request, message):
    return render_to_response(
                        "error.html",
                        {'error_message': message},
                        context_instance=RequestContext(request))
