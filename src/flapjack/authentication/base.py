# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import abc
from django.contrib.auth.models import AnonymousUser
from ..http import HttpResponse, constants


class Base(object):
    """Describes the base authentication protocol.
    """

    def __init__(self, require_active=True, **kwargs):
        """
        Initializes any configuration properties specific for this
        authentication protocol.
        """
        #! Whether to require users to have `is_active` flags in django set to
        #! `True`.
        self.require_active = require_active

    def authenticate(self, request):
        """Gets the a user if they are authenticated; else None.

        @retval None           Unable to authenticate.
        @retval AnonymousUser  Able to authenticate but failed.
        @retval User           User object representing the curretn user.
        """
        header = request.META.get('HTTP_AUTHORIZATION')
        try:
            method, credentials = header.split(' ', 1)
            if not self.can_authenticate(method, credentials):
                # We are unable to (for whatever reason) make an informed
                # authentication descision using these as criterion
                return None

            user = self.get_user(method, credentials)
            if user is None or not self.is_active(user):
                # No user was retrieved or the retrieved user was deemed
                # to be inactive.
                return AnonymousUser()

            return user

        except AttributeError:
            # Something went wrong and we were unable to authenticate;
            # possible reasons include:
            #   - No `authorization` header present
            return None

    @abc.abstractmethod
    def can_authenticate(self, method, credentials):
        """Checks if authentication can be asserted with reasonable reliance.

        @retval True
            Indicates that this authentication protocol can assert a user
            with the given credentials with a reasonable confidence.

        @retval False
            Indicates that this authentication protocol cannot assert a user
            and that the authentication process should continue on to the
            next available authentication protocol.
        """
        pass

    @abc.abstractmethod
    def get_user(self, method, credentials):
        """Retrieves a user using the provided credentials.

        @return
            Returns either the currently authenticated user
            or `AnonymousUser`.
        """
        pass

    def is_active(self, user):
        """Checks if the user is active; served as a point of extension."""
        return user.is_active if self.require_active else False

    @property
    def unauthenticated(self):
        """What response to return upon failing authentication."""
        return HttpResponse(status=constants.FORBIDDEN)