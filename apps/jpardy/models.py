from django.db import models
from django.contrib.auth.models import User

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
        ordering = ['name']
        verbose_name_plural = "categories"

class Question(models.Model):
    question = models.TextField(max_length=200, blank=True)
    answer = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(Category, editable=False)
    daily_double = models.BooleanField(default=False)

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
