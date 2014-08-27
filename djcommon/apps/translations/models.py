# encoding: utf-8

from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet

from djcommon.models import LanguageMixin


class TranslationQuerySet(QuerySet):

    def language(self, language_code):
        return self.filter(language=language_code)


class TranslationManager(models.Manager):

    def get_queryset(self):
        return TranslationQuerySet(self.model, using=self._db)


class TranslationMixin(LanguageMixin):

    translations = models.ManyToManyField('self')
    objects =  TranslationManager()

    def get_translations(self):
        return self.translations.all()

    def get_available_languages(self):
        return self.get_translations().values_list('language', flat=True).distinct()

    class Meta:
        abstract = True