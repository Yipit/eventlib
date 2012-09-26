# eventlib - Copyright (c) 2012  Yipit, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Implementation of the basic operations for the eventlib"""


import logging
from collections import OrderedDict
from importlib import import_module
from datetime import datetime

from . import conf
from .util import get_ip
from .ejson import loads
from .exceptions import (
    ValidationError, EventNotFoundError, InvalidEventNameError
)


HANDLER_REGISTRY = OrderedDict()

HANDLER_METHOD_REGISTRY = []

logger = logging.getLogger('event')


def parse_event_name(name):
    """Returns the python module and obj given an event name
    """
    try:
        app, event = name.split('.')
        return '{}.events'.format(app), event
    except ValueError:
        raise InvalidEventNameError(
            (u'The name "{}" is invalid. '
             u'Make sure you are using the "app.KlassName" format'
             ).format(name))


def find_event(name):
    """Actually import the event represented by name

    Raises the `EventNotFoundError` if it's not possible to find the
    event class refered by `name`.
    """
    try:
        module, klass = parse_event_name(name)
        return getattr(import_module(module), klass)
    except (ImportError, AttributeError):
        raise EventNotFoundError(
            ('Event "{}" not found. '
             'Make sure you have a class called "{}" inside the "{}" '
             'module.'.format(name, klass, module)))


def cleanup_handlers(event=None):
    """Remove handlers of a given `event`. If no event is informed, wipe
    out all events registered.

    Be careful!! This function is intended to help when writing tests
    and for debugging purposes. If you call it, all handlers associated
    to an event (or to all of them) will be disassociated. Which means
    that you'll have to reload all modules that teclare handlers. I'm
    sure you don't want it.
    """
    if event:
        del HANDLER_REGISTRY[event]
    else:
        HANDLER_REGISTRY.clear()


def find_handlers(event_name):
    """Small halper to find all handlers associated to a given event

    If the event can't be found, an empty list will be returned, since
    this is an internal function and all validation against the event
    name and its existence was already performed.
    """
    handlers = HANDLER_REGISTRY.get(find_event(event_name), [])
    handlers.extend(HANDLER_REGISTRY.get(event_name, []))
    return handlers


def process(event_name, data):
    """Iterates over the event handler registry and execute each found
    handler.

    It takes the event name and its its `data`, passing the return of
    `ejson.loads(data)` to the found handlers.
    """
    deserialized = loads(data)
    event_cls = find_event(event_name)
    event = event_cls(event_name, deserialized)
    try:
        event.clean()
    except ValidationError as exc:
        logger.warning(
            "The event system just got an exception while cleaning "
            "data for the event '{}'\ndata: {}\nexc: {}".format(
                event_name, data, str(exc)))
        return

    for handler in find_handlers(event_name):
        try:
            handler(deserialized)
        except Exception as exc:
            logger.warning(
                (u'One of the handlers for the event "{}" has failed with the '
                 u'following exception: {}').format(event_name, str(exc)))
            if conf.DEBUG:
                raise exc


def get_default_values(data):
    """Return all default values that an event should have"""
    request = data.get('request')
    result = {}
    result['__datetime__'] = datetime.now()
    result['__ip_address__'] = request and get_ip(request) or '0.0.0.0'
    return result


def filter_data_values(data):
    """Remove special values that log function can take

    There are some special values, like "request" that the `log()`
    function can take, but they're not meant to be passed to the celery
    task neither for the event handlers. This function filter these keys
    and return another dict without them.
    """
    banned = ('request',)
    return {key: val for key, val in data.items() if not key in banned}
