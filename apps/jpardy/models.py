from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, editable=False)
    played = models.BooleanField(default=False, editable=False)

class Question(models.Model):
    question = models.TextField(max_length=200)
    answer = models.TextField(max_length=200)
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
