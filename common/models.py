# -*- coding: utf-8 -*-

from django.db import models


class OrderableModel(models.Model):
    """
    Add extra field and default ordering column for and inline orderable model
    """
    position = models.IntegerField(blank=True, null=True)

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
  date_created = models.DateTimeField(auto_now_add=True)
  date_modified = models.DateTimeField(auto_now=True)

  class Meta:
      abstract = True