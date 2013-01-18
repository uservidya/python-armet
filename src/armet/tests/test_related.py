# -*- coding: utf-8 -*-
import hashlib
from django.test.client import RequestFactory
from armet import http, exceptions
from armet.utils import test
from armet import resources, encoders
from django import forms
from django.db import models
from . import models as local_models
from . import api
from django.utils import timezone
import six


class RelatedTest(test.TestCase):

    def setUp(self):
        self.booth = local_models.Booth.objects.create(name="Steve")

        data = {'question': "...", 'pub_date': timezone.now()}
        self.booth.polls.add(local_models.Poll.objects.create(**data))
        self.booth.polls.add(local_models.Poll.objects.create(**data))
        self.booth.polls.add(local_models.Poll.objects.create(**data))

    def test_property(self):
        request = RequestFactory().get('/cushion/5')
        resource = api.Cushion(request=request, slug=5)

        model = local_models.Cushion(color="Bob",
            booth=local_models.Booth(name='Red'))

        data = resource.prepare(model)

        self.assertIsInstance(data['poll'], six.string_types)

    def test_many_to_many(self):
        request = RequestFactory().get('/booth/1')
        resource = api.Booth(request=request, slug=1)
        data = resource.prepare(self.booth)

        self.assertIsInstance(data['polls'][0], six.string_types)
        self.assertIsInstance(data['polls'][1], six.string_types)

    def test_missing_resource(self):
        try:
            class AppleModel(models.Model):
                name = models.CharField(max_length=30)

            class FruitModel(models.Model):
                apple = models.ManyToManyField(AppleModel)

            class FruitResource(resources.Model):
                model = FruitModel
                canonical = False
                resource_uri = None

            request = RequestFactory().get('/fruit/1')
            resource = FruitResource(request=request, slug=1)
            data = resource.prepare({'apple': 3})

        except exceptions.NotFound:
            pass

        except:
            self.fail()