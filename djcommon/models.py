# coding: utf-8

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _


class OrderableModel(models.Model):
    """
    Add extra field and default ordering column for and inline orderable model
    """
    position = models.IntegerField(blank=True, null=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('position',)

    def save(self, force_insert=False, force_update=False, using=None):
        """
        Calculate position (max+1) for new records
        """
        if not self.position:
            max = self.__class__.objects.filter().aggregate(models.Max('position'))
            try:
                self.position = max['position__max'] + 1
            except TypeError:
                self.position = 1
        return super(OrderableModel, self).save(force_insert=force_insert, force_update=force_update, using=using)


class TimeStampedModel(models.Model):
  date_created = models.DateTimeField(_("date/time created"), auto_now_add=True)
  date_modified = models.DateTimeField(_("date/time modified"), auto_now=True)

  class Meta:
      abstract = True


class LanguageMixin(models.Model):
  language = models.CharField(max_length=7, choices=settings.LANGUAGES, db_index=True)

  class Meta:
      abstract = True


class SubclassQuerySet(QuerySet):

    def iterator(self):
        for obj in super(SubclassQuerySet, self).iterator():
            yield obj.get_subclass_object()


class SubclassManager(models.Manager):

    def get_query_set(self):
        return SubclassQuerySet(self.model)


class ParentModel(models.Model):
    _subclass_name = models.CharField(max_length=100, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self._subclass_name = self.get_subclass_name()
        super(ParentModel, self).save(*args, **kwargs)

    def get_subclass_name(self):
        if type(self) is self.get_parent_model():
            return self._subclass_name
        if self._meta.proxy:
            return self.__class__.__name__.lower()
        return self.get_parent_link().related_query_name()

    def get_subclass_object(self):
        if self._meta.proxy:
            pass
        else:
            return getattr(self, self.get_subclass_name())

    def get_parent_link(self):
        return self._meta.parents[self.get_parent_model()]

    def get_parent_model(self):
        raise NotImplementedError

    def get_parent_object(self):
        return getattr(self, self.get_parent_link().name)