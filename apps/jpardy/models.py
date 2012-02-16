from django.db import models
from django.contrib.auth.models import User
from django.test import TestCase
from django.db import IntegrityError
from django.utils import simplejson
from django.template.defaultfilters import truncatewords

class Category(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, editable=False)
    played = models.BooleanField(default=False, editable=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        self._verify_questions_exist()

    def _verify_questions_exist(self):
        for i in (100, 200, 300, 400, 500):
            Question.objects.get_or_create(category=self, value=i)

    def _get_number_of_questions(self):
        return 5 - len(self.question_set.filter(question=''))
    number_of_questions = property(_get_number_of_questions)

    class Meta:
        ordering = ['played', 'name']
        verbose_name_plural = "categories"


class Game(models.Model):
    owner = models.ForeignKey(User, editable=False, related_name='games_owned')
    categories = models.ManyToManyField(Category, through='CategoryInGame')
    players = models.ManyToManyField(User, related_name='games_played', through='PlayerInGame')
    create_date = models.DateTimeField(auto_now_add=True)
    final_question = models.ForeignKey('FinalQuestion')

    def get_json_data(self):
        data = {}
        data['pk'] = self.pk
        
        data['players'] = {}
        for pig in PlayerInGame.objects.filter(game=self):
            data['players'][pig.pk] = {}
            data['players'][pig.pk]['username'] = pig.player.username
            data['players'][pig.pk]['first_name'] = pig.player.first_name
            data['players'][pig.pk]['last_name'] = pig.player.last_name
            data['players'][pig.pk]['score'] = pig.score

        data['categories'] = {}
        for cig in CategoryInGame.objects.filter(game=self):
            data['categories'][cig.pk] = {}
            data['categories'][cig.pk]['name'] = cig.category.name

        data['questions'] = {}
        for qig in QuestionInGame.objects.filter(category_in_game__game=self):
            data['questions'][qig.pk] = {}
            data['questions'][qig.pk]['pk'] = qig.pk
            data['questions'][qig.pk]['question'] = qig.question.question
            data['questions'][qig.pk]['answer'] = qig.question.answer
            data['questions'][qig.pk]['value'] = qig.question.value
            data['questions'][qig.pk]['daily_double'] = qig.daily_double
            data['questions'][qig.pk]['category'] = qig.category_in_game.pk
            data['questions'][qig.pk]['asked'] = qig.asked

            if len(QuestionInGameResult.objects.filter(question_in_game=qig)) == 0:
                data['questions'][qig.pk]['result'] = None
            else:
                data['questions'][qig.pk]['result'] = {}
                for qigr in QuestionInGameResult.objects.filter(question_in_game=qig):
                    data['questions'][qig.pk]['result'][qigr.player.pk] = qigr.score_change

        data['final_question'] = {}
        data['final_question']['pk'] = self.final_question.pk
        data['final_question']['question'] = self.final_question.question
        data['final_question']['answer'] = self.final_question.answer
        data['final_question']['category'] = self.final_question.category

        return simplejson.dumps(data)

    def load_json_data(self, json_string):
        data = simplejson.loads(json_string)
        
        qig = QuestionInGame.objects.get(pk=data['pk'])
        qig.asked = data['asked']
        qig.save()

        for qigr in QuestionInGameResult.objects.filter(question_in_game=qig):
            if qigr.player.pk in data['result']:
                qigr.player.score -= qigr.score_change
                qigr.score_change = data['result'][qigr.player.pk]
                qigr.player.score += qigr.score_change
                qigr.save()
                qigr.player.save()

                del data['result'][qigr.player.pk]
            else:
                qigr.player.score -= qigr.score_change
                qigr.player.save()
                qigr.delete()

        for k, v in data['result'].items():
            qigr = QuestionInGameResult.objects.create(
                question_in_game=qig,
                player=PlayerInGame.objects.get(pk=k))

            qigr.score_change = v
            qigr.player.score += v
            qigr.save()
            qigr.player.save()


class PlayerInGame(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(User)
    score = models.SmallIntegerField(default=0)


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


class FinalQuestion(models.Model):
    owner = models.ForeignKey(User, editable=False)
    question = models.TextField(max_length=200)
    answer = models.CharField(max_length=50)
    category = models.CharField(max_length=50)

    def __unicode__(self):
        return truncatewords(self.question, 5)


class QuestionInGame(models.Model):
    category_in_game = models.ForeignKey('CategoryInGame')
    question = models.ForeignKey(Question)
    daily_double = models.BooleanField(default=False)
    asked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('category_in_game', 'question')


class QuestionInGameResult(models.Model):
    question_in_game = models.ForeignKey(QuestionInGame)
    player = models.ForeignKey(PlayerInGame)
    score_change = models.SmallIntegerField(default=0)


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
                                category_in_game=self,
                                question=self.category.question_set.get(value=i))

    class Meta:
        unique_together = ('game', 'category')


class GameTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.user = User.objects.get(username='user1')
        self.guitar_cat = Category.objects.get(name='Guitar Brands')
        self.candy_cat = Category.objects.get(name='Name That Candy')
        self.game = Game.objects.create(owner=self.user)

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
