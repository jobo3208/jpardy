from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.http import HttpResponse

from apps.jpardy.models import *
from apps.jpardy.forms import *
from django.forms.models import inlineformset_factory

@login_required
def home(request):
    return render(request,
                  'home.html')

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

    return render(request,
                  'manage.html',
                  {'categories': categories,
                   'category_form': category_form,})

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
        form = CategoryNameForm(request.POST, instance=category)
        formset = CategoryFormSet(request.POST, instance=category)
        if form.is_valid and formset.is_valid():
            form.save()
            formset.save()
            return redirect('/manage/')
    else:
        form = CategoryNameForm(instance=category)
        formset = CategoryFormSet(instance=category)

    return render(request,
                  "edit.html", 
                  {"form": form,
                   "formset": formset,
                   "category": category,})

@login_required
def delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.user != category.user:
        return error(request, "You do not own this category.")

    if request.method == 'POST':
        category.delete()
        return redirect('/manage/')

    return render(request,
                  "confirm_delete.html", 
                  {"category": category,})

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
        if len(category_choices) == 0:
            form = None
        else:
            form = SelectCategoryForm(queryset=category_choices)

    return render(request,
                  "select_categories.html",
                  {"form": form})

def error(request, message):
    return render(request,
                  "error.html",
                  {'error_message': message})
