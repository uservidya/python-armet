# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import wsgi_intercept
import os
from wsgi_intercept.httplib2_intercept import install


def setup():
    # Install the WSGI interception layer on top of httplib2.
    install()

    # Ensure the settings are pointed to correctly.
    # Ensure the settings are pointed to correctly.
    module = 'tests.{}.settings'.format('django_django')
    os.environ["DJANGO_SETTINGS_MODULE"] = module

    # Initialize the database tables.
    from django.db import connections, DEFAULT_DB_ALIAS
    connection = connections[DEFAULT_DB_ALIAS]
    connection.creation.create_test_db()

    # Install the test fixture.
    from django.core.management import call_command
    call_command('loaddata', 'test', verbosity=0, skip_validation=True)

    # Set the WSGI application to intercept to.
    from django.core.wsgi import get_wsgi_application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, get_wsgi_application)


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
