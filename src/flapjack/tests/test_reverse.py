# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import os
from django.utils.unittest import TestCase
from django.test.client import RequestFactory
from . import api


class ReverseTestCase(TestCase):

    def test_list(self):
        """Tests for `/poll`."""
        request = RequestFactory().get('/poll')
        resource = api.Poll(request)

        self.assertEqual(resource.url, '/poll')
        self.assertEqual(resource.slug, None)

    def test_slug(self):
        """Tests for `/poll/:id`."""
        slug = '1'
        url = '/poll/{}'.format(slug)
        request = RequestFactory().get(url)
        resource = api.Poll(request, slug=slug)

        self.assertEqual(resource.slug, slug)
        self.assertEqual(resource.url, url)

    def test_slug_long(self):
        """Tests for `/poll/:id`."""
        slug = '1239853297572983'
        url = '/poll/{}'.format(slug)
        request = RequestFactory().get(url)
        resource = api.Poll(request, slug=slug)

        self.assertEqual(resource.slug, slug)
        self.assertEqual(resource.url, url)

    def test_path_attribute(self):
        """Tests for `/poll/:id/question`."""
        slug = '269'
        path = 'question'
        url = '/poll/{}/{}'.format(slug, path)
        request = RequestFactory().get(url)
        resource = api.Poll(request, slug=slug, path=[path])

        self.assertEqual(resource.slug, slug)
        self.assertEqual(resource.path, [path])
        self.assertEqual(resource.url, url)

    def test_path_long(self):
        """Tests for `/poll/:id/choices/:id`.

        Should resolve to the identified choice as long as it is related to the
        identified poll; else, 404.
        """
        slug = '269'
        path = ['choices', '561']
        url = '/poll/{}/{}'.format(slug, os.path.join(*path))
        request = RequestFactory().get(url)
        resource = api.Poll(request, slug=slug, path=path)

        self.assertEqual(resource.slug, slug)
        self.assertEqual(resource.path, path)
        self.assertEqual(resource.url, url)

    def test_path_nested(self):
        """Tests for `/poll/:id/choices/:id/poll/question/:index`.

        Should resolve to the nth character of the question of the poll of
        the identified choice as long as it is related to the identified
        poll; else, 404.
        """
        slug = '262627'
        path = ['choices', '2858', 'poll', 'question', '15678']
        url = '/poll/{}/{}'.format(slug, os.path.join(*path))
        request = RequestFactory().get(url)
        resource = api.Poll(request, slug=slug, path=path)

        self.assertEqual(resource.slug, slug)
        self.assertEqual(resource.path, path)
        self.assertEqual(resource.url, url)

    def test_path_local_single(self):
        """Tests for `/choice/:id/poll`."""
        slug = '262627'
        url = '/choice/{}/poll'.format(slug)
        request = RequestFactory().get(url)
        parent = api.Choice(request, slug=slug)
        resource = api.Poll(request, slug='32', local=True,
            parent=(parent, 'poll', slug))

        self.assertEqual(parent.slug, slug)
        self.assertEqual(resource.slug, '32')
        self.assertEqual(resource.url, url)

    def test_path_local_many(self):
        """Tests for `/poll/:id/choices/:id`."""
        poll = '262627'
        choice = '231'
        url = '/poll/{}/choices/{}'.format(poll, choice)
        request = RequestFactory().get(url)
        parent = api.Poll(request, slug=poll)
        resource = api.Choice(request, slug=choice, local=True,
            parent=(parent, "choices", poll))

        self.assertEqual(resource.slug, choice)
        self.assertEqual(parent.slug, poll)
        self.assertEqual(resource.url, url)

    def test_path_local_single_attribute(self):
        """Tests for `/choice/:id/poll`."""
        slug = '262627'
        url = '/choice/{}/poll/question'.format(slug)
        path = ['question']
        request = RequestFactory().get(url)
        parent = api.Choice(request, slug=slug)
        resource = api.Poll(request, slug='32', local=True, path=path,
            parent=(parent, 'poll', slug))

        self.assertEqual(parent.slug, slug)
        self.assertEqual(resource.slug, '32')
        self.assertEqual(resource.url, url)
        self.assertEqual(resource.path, path)

    def test_path_local_many_attribute(self):
        """Tests for `/poll/:id/choices/:id/choice_text`."""
        poll = '262627'
        choice = '231'
        path = ['choice_text']
        url = '/poll/{}/choices/{}/choice_text'.format(poll, choice)
        request = RequestFactory().get(url)
        parent = api.Poll(request, slug=poll)
        resource = api.Choice(request, slug=choice, path=path, local=True,
            parent=(parent, "choices", poll))

        self.assertEqual(resource.slug, choice)
        self.assertEqual(parent.slug, poll)
        self.assertEqual(resource.url, url)
        self.assertEqual(resource.path, path)

    def test_path_local_nested(self):
        """Tests for `/poll/:id/choices/:id/poll`."""
        poll = '262627'
        choice = '231'
        url = '/poll/{}/choices/{}/poll'.format(poll, choice)
        request = RequestFactory().get(url)
        parent_poll = api.Poll(request, slug=poll)
        parent_choice = api.Choice(request, slug=choice, local=True,
            parent=(parent_poll, "choices", poll))
        resource = api.Poll(request, slug=poll, local=True,
            parent=(parent_choice, "poll", choice))

        self.assertEqual(resource.slug, poll)
        self.assertEqual(parent_choice.slug, choice)
        self.assertEqual(parent_poll.slug, poll)
        self.assertEqual(resource.url, url)

    def test_path_local_nested(self):
        """Tests for `/poll/:id/choices/:id/poll/question`."""
        poll = '262627'
        choice = '231'
        path = ['question']
        url = '/poll/{}/choices/{}/poll/question'.format(poll, choice)
        request = RequestFactory().get(url)
        parent_poll = api.Poll(request, slug=poll)
        parent_choice = api.Choice(request, slug=choice, local=True,
            parent=(parent_poll, "choices", poll))
        resource = api.Poll(request, slug=poll, local=True, path=path,
            parent=(parent_choice, "poll", choice))

        self.assertEqual(resource.slug, poll)
        self.assertEqual(parent_choice.slug, choice)
        self.assertEqual(parent_poll.slug, poll)
        self.assertEqual(resource.url, url)
        self.assertEqual(resource.path, path)
