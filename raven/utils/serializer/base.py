"""
raven.utils.serializer.base
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from raven.utils.encoding import to_string, to_unicode
from raven.utils.serializer.manager import register
from types import ClassType, TypeType
from uuid import UUID


def has_sentry_metadata(value):
    try:
        return callable(value.__getattribute__('__sentry__'))
    except:
        return False


class Serializer(object):
    types = ()

    def __init__(self, manager):
        self.manager = manager

    def can(self, value):
        return isinstance(value, self.types)

    def serialize(self, value):
        return value

    def recurse(self, value):
        return self.manager.transform(value)


@register
class IterableSerializer(Serializer):
    types = (tuple, list, set, frozenset)

    def serialize(self, value):
        try:
            return type(value)(self.recurse(o) for o in value)
        except Exception:
            # We may be dealing with something like a namedtuple
            class value_type(list):
                __name__ = type(value).__name__
            return value_type(self.recurse(o) for o in value)


@register
class UUIDSerializer(Serializer):
    types = (UUID,)

    def serialize(self, value):
        return repr(value)


@register
class DictSerializer(Serializer):
    types = (dict,)

    def serialize(self, value):
        return dict((to_string(k), self.recurse(v)) for k, v in value.iteritems())


@register
class UnicodeSerializer(Serializer):
    types = (unicode,)

    def serialize(self, value):
        return to_unicode(value)


@register
class StringSerializer(Serializer):
    types = (str,)

    def serialize(self, value):
        return to_string(value)


@register
class TypeSerializer(Serializer):
    types = (ClassType, TypeType,)

    def can(self, value):
        return not super(TypeSerializer, self).can(value) and has_sentry_metadata(value)

    def serialize(self, value):
        return self.recurse(value.__sentry__())


@register
class BooleanSerializer(Serializer):
    types = (bool,)

    def serialize(self, value):
        return bool(value)


@register
class FloatSerializer(Serializer):
    types = (float,)

    def serialize(self, value):
        return float(value)


@register
class IntegerSerializer(Serializer):
    types = (int,)

    def serialize(self, value):
        return int(value)


@register
class LongSerializer(Serializer):
    types = (long,)

    def serialize(self, value):
        return long(value)