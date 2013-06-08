# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import collections
import six


class Attribute(object):
    """Generic attribute; (de)serialzied as text.
    """

    def __init__(self, path=None, **kwargs):
        """Initializes this attribute with the given properties."""
        #! If this attribute can be read via direct
        #! access (eg. GET /resource/1/attribute)
        #! @warning Not implemented.
        self.readable = kwargs.get('readable', True)

        #! If this attribute can be written via direct
        #! access (eg. PUT /resource/1/attribute) or modification of the
        #! resource (eg. PUT /resource/1 or PATCH /resource/1).
        #! @warning Not implemented.
        self.writable = kwargs.get('writable', True)

        #! If this attribute is included in the resource body.
        #! @warning Not implemented.
        self.include = kwargs.get('include', True)

        #! If this attribute can accept null as a value.
        #! @warning Not implemented.
        self.null = kwargs.get('null', True)

        #! If this attribute must have some value.
        #! @warning Not implemented.
        self.required = kwargs.get('required', True)

        #! If this attribute is represented as a collection (aka. array).
        self.collection = kwargs.get('collection', False)

        #! The path reference of where to find this attribute on an
        #! item (eg. 'name' references the name key if the read method returns
        #! a dictionary.)
        #!
        #! The path may be dot-separated to indicate simple traversal.
        #! Eg. user.name could be obj['user'].name
        self.path = path

        if self.path:
            # Explode the path into segments.
            self._segments = path.split('.')

            # Initialize the accessors array.
            self._accessors = []

    def clone(self):
        # Construct a new this.
        return self.__class__(**self.__dict__)

    def _make_accessor(self, path, cls, instance):
        # Attempt to get an unbound class property
        # that may be a descriptor.
        obj = getattr(cls, path, None)
        if obj is not None:
            if hasattr(obj, '__call__'):
                # The descriptor is callable.
                return obj.__call__

            if hasattr(obj, '__get__'):
                # This has a data descriptor.
                return lambda o, c=cls, g=obj.__get__: g(o, c)

        else:
            # Check for another kind of descriptor.
            descriptor = cls.__dict__.get(path)
            if descriptor and hasattr(descriptor, '__get__'):
                return descriptor.__get__

        if issubclass(cls, collections.Mapping):
            return lambda o, n=path: o.get(n)

        # No alternative; let's pretend this will work (which it will
        # most of the time).
        return lambda o, n=path: o.__dict__.get(n)

    def get(self, value):
        """Retrieves the value of this attribute from the passed object."""
        if not self.path:
            # If we do not have a path; we cannot automatically
            # resolve our value; return nothing.
            return None

        for accessor in self._accessors:
            # Iterate and resolve the attribute path.
            value = accessor(value)

        if self._segments and value is not None:
            # Value isn't none and we still have additional segments left
            # to resolve into accessors.
            while self._segments:
                if value is None:
                    # We no longer have a value to use to attempt
                    # to resolve additional segments; bail for now.
                    break

                # Remove any path segments that have been resolved
                # into accessors.
                segment = self._segments.pop(0)

                # Build the accessor corresponding to this path
                # segment.
                accessor = self._make_accessor(
                    segment, value.__class__, value)

                # Append the accessor.
                self._accessors.append(accessor)

                # Utilize the accessor now.
                value = accessor(value)

        # Return what has been accessed.
        return value

    def prepare(self, value):
        """Prepares the value for serialization."""
        return value

    def clean(self, value):
        """Cleans the value in preparation for deserialization."""
        return value


class TextAttribute(Attribute):
    """Represents text.
    """

    def prepare(self, value):
        """Stringifies the value."""
        return str(value) if value is not None else None


class BooleanAttribute(Attribute):
    """
    Represents a boolean; prepared as a python bool and cleaned as
    an actual bool in most deserializers.
    """

    #! Textual values accepted for `True`.
    TRUE = (
        'true',
        't',
        'yes',
        'y',
        'on',
        '1'
    )

    #! Textual values accepted for `False`.
    FALSE = (
        'false',
        'f',
        'no',
        'n',
        'off',
        '0'
    )

    def clean(self, value):
        if value is None:
            # Value is nothing; return it.
            return value

        if value is True or value is False:
            # Value is a python boolean; just return it.
            return value

        if value.strip().lower() in self.TRUE:
            # Some sort of truthy value.
            return True

        if value.strip().lower() in self.FALSE:
            # Some sort of falsy value.
            return False

        # Neither true or false matches; return a boolifyed version of
        # whatever we have.
        return bool(value)


class IntegerAttribute(Attribute):
    """Represents an integer; serialzied as a python integer.
    """

    def clean(self, value):
        if isinstance(value, six.string_types):
            # Strip the string of whitespace
            value = value.strip()

        try:
            # Attempt to coerce whatever we have as an int.
            return int(value)

        except ValueError:
            # Failed to do so.
            return None
