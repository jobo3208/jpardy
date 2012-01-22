from django.db import models
from django.contrib.auth.models import User
from django.test import TestCase
from django.db import IntegrityError

class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, editable=False)
    played = models.BooleanField(default=False, editable=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        self._verify_questions_exist()

    def _verify_questions_exist(self):
        for i in (100, 200, 300, 400, 500):
            Question.objects.get_or_create(category=self, value=i)

    def number_of_questions(self):
        return 5 - len(self.question_set.filter(question=''))

    class Meta:
        ordering = ['played', 'name']
        verbose_name_plural = "categories"


class Game(models.Model):
    user = models.ForeignKey(User, editable=False)
    categories = models.ManyToManyField(Category, through='CategoryInGame')


class Question(models.Model):
    question = models.TextField(max_length=200, blank=True)
    answer = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(Category, editable=False)

    VALUE_CHOICES = (
        (100, '100'),
        (200, '200'),
        (300, '300'),
        (400, '400'),
        (500, '500'),
    )
    value = models.PositiveSmallIntegerField(choices=VALUE_CHOICES)

    def __unicode__(self):
        return "%s: %d: %s" % (self.category.name, self.value, self.question)

    class Meta:
        ordering = ['category__name', 'value']


class QuestionInGame(models.Model):
    category_use_in_game = models.ForeignKey('CategoryInGame')
    question = models.ForeignKey(Question)
    daily_double = models.BooleanField(default=False)
    played = models.BooleanField(default=False)
    answered_by = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        unique_together = ('category_use_in_game', 'question')


class CategoryInGame(models.Model):
    game = models.ForeignKey(Game)
    category = models.ForeignKey(Category)
    questions = models.ManyToManyField(Question, through=QuestionInGame)

    def save(self, *args, **kwargs):
        super(CategoryInGame, self).save(*args, **kwargs)
        self._verify_questions_exist()

    def _verify_questions_exist(self):
        for i in (100, 200, 300, 400, 500):
            QuestionInGame.objects.get_or_create(
                                category_use_in_game=self,
                                question=self.category.question_set.get(value=i))

    class Meta:
        unique_together = ('game', 'category')


class GameTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.user = User.objects.get(username='user1')
        self.guitar_cat = Category.objects.get(name='Guitar Brands')
        self.candy_cat = Category.objects.get(name='Name That Candy')
        self.game = Game.objects.create(user=self.user)

    def test_question_creation(self):
        cig = CategoryInGame.objects.create(game=self.game, category=self.guitar_cat)
        self.assertQuerysetEqual(cig.questions.all(), map(repr, self.guitar_cat.question_set.all()))

    def test_duplicate_category_in_game(self):
        cig = CategoryInGame.objects.create(game=self.game, category=self.guitar_cat)
        with self.assertRaises(IntegrityError):
            CategoryInGame.objects.create(game=self.game, category=self.guitar_cat)

    def test_delete_game(self):
        cig = CategoryInGame.objects.create(game=self.game, category=self.guitar_cat)
        self.game.delete()
        self.assertEqual(len(QuestionInGame.objects.all()), 0)
        self.assertEqual(len(CategoryInGame.objects.all()), 0)
