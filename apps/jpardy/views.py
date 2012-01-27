from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.http import HttpResponse

from apps.jpardy.models import *
from apps.jpardy.forms import *

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
            new_category.owner = request.user
            new_category.save()

            # Give a blank form if we succeeded.
            category_form = CategoryNameForm()
    else:
        category_form = CategoryNameForm()

    categories = Category.objects.filter(owner=request.user)

    return render(request,
                  'manage.html',
                  {'categories': categories,
                   'category_form': category_form,})

@login_required
def edit(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.user != category.owner:
        return error(request, "You do not own this category.")

    if request.method == 'POST':
        form = CategoryNameForm(request.POST, instance=category)
        formset = CategoryFormSet(request.POST, instance=category)

        if form.is_valid and formset.is_valid():
            form.save()
            formset.save()

            return redirect(manage)

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

    if request.user != category.owner:
        return error(request, "You do not own this category.")

    if request.method == 'POST':
        category.delete()

        return redirect(manage)

    return render(request,
                  "confirm_delete.html", 
                  {"category": category,})

@login_required
def games(request):
    my_games = request.user.games_owned.all()

    return render(request,
                  "games.html",
                  {"games": my_games})

@login_required
def create_game(request):
    # We have to use this convoluted way of getting only "full" categories.
    category_choice_pks = [cat.pk for 
                                cat in 
                                    Category.objects.filter(owner=request.user) if
                                        cat.number_of_questions == 5]
    category_choices = Category.objects.filter(pk__in=category_choice_pks)

    if request.method == 'POST':
        form = InitialGamePrepForm(request.POST, category_qs=category_choices)

        if form.is_valid():
            game = Game.objects.create(owner=request.user)
            game.save()

            for player in form.cleaned_data['players']:
                PlayerInGame.objects.create(game=game,
                                            player=player)

            for category in form.cleaned_data['categories']:
                CategoryInGame.objects.create(game=game,
                                              category=category)

            return redirect(set_daily_doubles, game.id)

    else:
        if len(category_choices) == 0:
            form = None
        else:
            form = InitialGamePrepForm(category_qs=category_choices)

    return render(request,
                  "prepare_game.html",
                  {"form": form})

@login_required
def set_daily_doubles(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        formset = GameDailyDoubleFormSet(request.POST, instance=game)
 
        if formset.is_valid():
            formset.save_all()
 
            return redirect(games)
 
    else:
        formset = GameDailyDoubleFormSet(instance=game)
 
    return render(request,
                  'select_daily_doubles.html',
                  {'game':game,
                   'categories':formset,})

def error(request, message):
    return render(request,
                  "error.html",
                  {'error_message': message})
