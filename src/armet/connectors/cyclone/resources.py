# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from cyclone import web
from cyclone import bottle
from . import http


class Handler(web.RequestHandler):
    """A cyclone request handler that forwards the request to armet.

    This involves overloading an internal method; `_execute_handler`.
    """

    def __init__(self, Resource, *args, **kwargs):
        # This must be set before we super, becuase that begins routing
        self.Resource = Resource
        return super(Handler, self).__init__(*args, **kwargs)

    def __route(self, path, *args, **kwargs):
        # Construct request and response wrappers.
        request = http.Request(self, path)
        response = None # http.Response(self)
        import ipdb; ipdb.set_trace()

        # Pass control off to the resource handler.
        self.Resource.view(request, response)

    def _execute_handler(self, _, args, kwargs):
        """
        This is copied directly from cyclone's repository with some
        minor changes to route all requests to a single method.

        For more information:
        https://github.com/fiorix/cyclone/blob/
        df43a89edd361d54f54e4d275ed5194512793789/cyclone/web.py#L1095-L1104
        """
        if not self._finished:
            # Decode arguemnts; changed slightly to use six (to be
            # python 3.x compliant).
            decode = self.decode_argument
            args = (decode(x) for x in args)
            kwargs = {k: decode(v, name=k) for k, v in six.iteritems(kwargs)}

            # Instead of calling each method, instead call the route handler
            deferred = self._deferred_handler(self.__route, *args, **kwargs)

            # Add callbacks; no changes here.
            deferred.addCallbacks(self._execute_success, self._execute_failure)
            self.notifyFinish().addCallback(self.on_connection_close)


class Resource(object):

    @classmethod
    def mount(cls, url, application=None, host_pattern=r'.*'):
        if application is None:
            # No application specified; add this to the bottle style handlers.
            bottle.route(cls.route(url)[0])(cls.handler)

        else:
            # Add the handler normally.
            application.add_handlers(host_pattern, (cls.route(url),))

    @classmethod
    def route(cls, url):
        return (r'{}/{}(.*)'.format(url, cls.meta.name), cls.handler)

    @classmethod
    def handler(cls, *args, **kwargs):
        return Handler(cls, *args, **kwargs)
