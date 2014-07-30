# encoding: utf-8

import unittest

from django.test import TestCase
from django.db import models
from djcommon.fields import HashField


class ExampleModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    hash = HashField(field_names='name,description')

	
class TestHashField(TestCase):

    def setUp(self):
        pass

    def test_string(self):
        instance = ExampleModel(name="Cafe", description="Lorem ipsum")
        hash_field = instance._meta.get_field_by_name('hash')[0]
        hash = hash_field.calculate_hash(instance)
        self.assertEqual(hash, 'e1500c515a62b8d6b846d074ad8625296e2fa6ef')

    def test_unicode(self):
        instance = ExampleModel(name=u"Café", description="Lorem ipsum")
        hash_field = instance._meta.get_field_by_name('hash')[0]
        hash = hash_field.calculate_hash(instance)
        self.assertEqual(hash, 'e17e90a9d2f5b1886390fd60e04888160472b919')

    def test_integer(self):
        instance = ExampleModel(name=1, description="Lorem ipsum")
        hash_field = instance._meta.get_field_by_name('hash')[0]
        hash = hash_field.calculate_hash(instance)
        self.assertEqual(hash, 'd0b5f95036dd47053e640b7de3b3f3bad4211b13')


if __name__ == '__main__':
    unittest.main()