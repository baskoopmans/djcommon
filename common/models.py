# -*- coding: utf-8 -*-

from django.db import models


class TimeStampedModel(models.Model):
  date_created = models.DateTimeField(auto_now_add=True)
  date_modified = models.DateTimeField(auto_now=True)

  class Meta:
      abstract = True