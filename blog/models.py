from django.db import models
from django.shortcuts import RequestContext
from django.contrib.auth.models import User
import os


class Article(models.Model):
    header = models.CharField(max_length=100, null=False, blank=False)
    content = models.TextField(null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False,)
    written_by = models.ForeignKey(User, related_name='written_by', null=False, blank=False)

    def is_saved(self, user):
        return SavedArticle.objects.filter(article=self, user=user)

    def is_favourite(self, user):
        return FavouriteArticle.objects.filter(article=self, user=user)

    @classmethod
    def list(cls):
        return cls.objects.all().order_by('-created')

    @classmethod
    def my_article_list(cls, user):
        return cls.objects.filter(written_by=user).order_by('-created')


class SavedArticle(models.Model):
    user = models.ForeignKey(User, related_name='saved_by', null=False, blank=False)
    article = models.ForeignKey(Article, related_name='saved_article', null=False, blank=False)

    @classmethod
    def article_list(cls, user):
        return cls.objects.filter(user=user)


class FavouriteArticle(models.Model):
    user = models.ForeignKey(User, related_name='favourite_by', null=False, blank=False)
    article = models.ForeignKey(Article, related_name='favourite_article', null=False, blank=False)

    @classmethod
    def article_list(cls, user):
        return cls.objects.filter(user=user)