# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import http, test


class GetTestCase(test.TestCase):

    def test_list(self):
        response, content = self.client.request('/api/poll')
