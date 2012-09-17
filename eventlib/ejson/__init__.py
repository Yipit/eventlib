# ejson - Copyright (c) 2012  Yipit, Inc
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Implementation of the RFC-00003-extensible-serialization proposal
"""

import json
from importlib import import_module
from collections import OrderedDict


__all__ = (
    'loads', 'dumps', 'deserialize',
    'register_serializer', 'register_deserializer',
    'cleanup_registry', 'cleanup_deserialization_registry',
)


REGISTRY = OrderedDict()
DESERIALIZE_REGISTRY = OrderedDict()


def loads(data):
    """Loads json data taking into account a registry of deserealizers.
    """
    return json.loads(data, object_hook=_convert_from)


def dumps(data):
    """A wrapper around `json.dumps` that can handle objects that json
    module is not aware.

    This function is aware of a list of custom serializers that can be
    registered by the API user, making it possible to convert any kind
    of object to types that the json library can handle.
    """
    return json.dumps(data, default=_converter)


def deserialize(klass, data):
    """Helper function to access a method that creates objects of a
    given `klass` with the received `data`.
    """
    handler = DESERIALIZE_REGISTRY.get(klass)
    if handler:
        return handler(data)
    raise TypeError("There is no deserializer registered to handle "
                    "instances of '{}'".format(klass.__name__))


def cleanup_registry():
    """Removes *all* entries in the serializer registry.

    Take care with this call, it is useful for writing tests or
    debugging purposes. I can't think in any other reason for using
    it. You have been advised.
    """
    REGISTRY.clear()


def cleanup_deserialization_registry():
    """Removes *all* entries in the deserializer registry.

    Take care with this call, it is useful for writing tests or
    debugging purposes. I can't think in any other reason for using
    it. You have been advised.
    """
    DESERIALIZE_REGISTRY.clear()


def register_serializer(klass):
    """Register a function that knows how to serialize a `klass`
    instance.

    This function can be used like a decorator. To do so, try the
    following:

        >>> @ejson.register_serializer(Klass)
        ... def serialize_klass(instance):
        ...     return {'attr': instance.attr}

    In another part of your code base, just do the following:

        >>> repr(ejson.deserialize(
        ...   '{"obj": {"__class__": "mod.Klass", "__value__": {"attr": 42}}}'
        ... ))
        'Klass(attr=42)'

    But the following is also enough:

        >>> repr(ejson.deserialize('{"obj": {"attr": 42}}'))
        'Klass(attr=42)'

    """
    def decorator(fun):
        REGISTRY[klass] = fun
        return fun
    return decorator


def register_deserializer(klass):
    """Register a function that knows builds a new instance of `klass`
    with the received attributres.

    This function can be used like a decorator. To do so, try the
    following:

        >>> @ejson.register_deserializer(Klass)
        ... def deserialize_klass(data):
        ...     return Klass(attr=data['attr']}

    In another part of your code base, just do the following:

        >>> obj = ejson.loads('{"mycustomobject": {"attr": 42}}')
        >>> repr(ejson.deserialize(Klass, obj))
        'Klass(attr=42)'
    """
    def decorator(fun):
        DESERIALIZE_REGISTRY[klass] = fun
        return fun
    return decorator


def _convert_from(data):
    """Internal function that will be hooked to the native `json.loads`

    Find the right deserializer for a given value, taking into account
    the internal deserializer registry.
    """
    try:
        module, klass_name = data['__class__'].rsplit('.', 1)
        klass = getattr(import_module(module), klass_name)
    except (ImportError, AttributeError, KeyError):
        # But I still haven't found what I'm looking for
        #
        # Waiting for three different exceptions here. KeyError will
        # raise if can't find the "__class__" entry in the json `data`
        # dictionary. ImportError happens when the module present in the
        # dotted name can't be resolved. Finally, the AttributeError
        # happens when we can find the module, but couldn't find the
        # class on it.
        return data
    return deserialize(klass, data['__value__'])


def _converter(data):
    """Internal function that will be passed to the native `json.dumps`.

    This function uses the `REGISTRY` of serializers and try to convert
    a given instance to an object that json.dumps can understand.
    """
    handler = REGISTRY.get(data.__class__)
    if handler:
        full_name = '{}.{}'.format(
            data.__class__.__module__,
            data.__class__.__name__)
        return {
            '__class__': full_name,
            '__value__': handler(data),
        }
    raise TypeError(repr(data) + " is not JSON serializable")
