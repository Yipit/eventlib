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

"""implementation of the RFC00001-event-log-spec proposal"""

# imports to get serializers registered
import eventlib.serializers  # pyflakes:ignore

import logging
from importlib import import_module
from datetime import datetime
from collections import OrderedDict
from celery.task import task

from .util import get_ip
from . import ejson
from . import conf
from exceptions import (
    ValidationError, EventNotFoundError, InvalidEventNameError
)

__version__ = '0.0.2'

__all__ = (
    'BaseEvent', 'handler', 'log',
    'ValidationError', 'EventNotFound', 'InvalidEventNameError',
)


HANDLER_REGISTRY = OrderedDict()

HANDLER_METHOD_REGISTRY = []

logger = logging.getLogger('event')


def _register_handler(event, fun):
    """Register a function to be an event handler"""
    if event in HANDLER_REGISTRY:
        HANDLER_REGISTRY[event].append(fun)
    else:
        HANDLER_REGISTRY[event] = [fun]
    return fun


class MetaEvent(type):
    """Takes care of the methods marked as handlers in an Event class"""

    def __new__(mcs, name, bases, attrs):
        newcls = type.__new__(mcs, name, bases, attrs)

        # Collecting the methods that were registered as handlers for
        # the class that we're processing right now.
        registered = \
            [m for m in attrs.items() if m[1] in HANDLER_METHOD_REGISTRY]

        # Just registering the method as a handler for the current class
        for method_name, func in registered:
            HANDLER_METHOD_REGISTRY.remove(func)
            _register_handler(newcls, getattr(newcls, method_name))
        return newcls


class BaseEvent(object):
    """Marker class for all events
    """

    __metaclass__ = MetaEvent

    def __init__(self, name, data):
        """Stores event name and data param as instance attributes"""
        self.name = name
        self.data = data

    def validate(self):
        """If you want to validate your data *BEFORE* sending it to the
        wire, override this method.

        If something goes wrong, you must raise the `ValidationError`
        exception.
        """

    def clean(self):
        """This method will be called by the event processor

        It must be overrided in the class that inherits from `BaseEvent'
        and raise `ValidationError` exceptions if something is wrong
        with the data received from the caller.
        """

    def validate_keys(self, *keys):
        """Validation helper to ensure that keys are present in data

        This method makes sure that all of keys received here are
        present in the data received from the caller.

        It is better to call this method in the `validate()` method of
        your event. Not in the `clean()` one, since the first will be
        called locally, making it easier to debug things and find
        problems.
        """
        current_keys = set(self.data.keys())
        needed_keys = set(keys)
        if not needed_keys.issubset(current_keys):
            raise ValidationError(
                'One of the following keys are missing from the '
                'event\'s data: {}'.format(
                    ', '.join(needed_keys.difference(current_keys)))
            )
        return True


def handler(param):
    """Decorator that associates a handler to an event class

    This decorator works for both methods and functions. Since it only
    registers the callable object and returns it without evaluating it.

    The name param should be informed in a dotted notation and should
    contain two informations: the django app name and the class
    name. Just like this:

        >>> @handler('deal.ActionLog')
        ... def blah(data):
        ...     sys.stdout.write('I love python!\n')

    You can also use this same decorator to mark class methods as
    handlers. Just notice that the class *must* inherit from
    `BaseEvent`.

        >>> class MyEvent(BaseEvent)
        ...     @handler('deal.ActionLog')
        ...     def another_blah(data):
        ...         sys.stdout.write('Stuff!\n')

    """
    if isinstance(param, basestring):
        return lambda f: _register_handler(param, f)
    else:
        HANDLER_METHOD_REGISTRY.append(param)
        return param


def log(name, data=None):
    """Entry point for the event lib that starts the logging process

    This function uses the `name` param to find the event class that
    will be processed to log stuff. This name must provide two
    informations separated by a dot: the app name and the event class
    name. Like this:

        >>> name = 'deal.ActionLog'

    The "ActionLog" is a class declared inside the 'deal.events' module
    and this function will raise an `EventNotFoundError` error if it's
    not possible to import the right event class.

    The `data` param *must* be a dictionary, otherwise a `TypeError`
    will be rised. All keys *must* be strings and all values *must* be
    serializable by the `json.dumps` function. If you need to pass any
    unsupported object, you will have to register a serializer
    function. Consult the RFC-00003-serialize-registry for more
    information.
    """
    data = data or {}
    data.update(get_default_values(data))

    event_cls = find_event(name)    # InvalidEventNameError, EventNotFoundError
    event = event_cls(name, data)
    event.validate()                # ValidationError
    data = filter_data_values(data)
    data = ejson.dumps(data)        # TypeError

    # We don't use celery when developing
    if conf.DEBUG:
        process(name, data)
    else:
        process.delay(name, data)


# ---- INTERNAL API ----


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


@task
def process(event_name, data):
    """Iterates over the event handler registry and execute each found
    handler.

    It takes the event name and its its `data`, passing the return of
    `ejson.loads(data)` to the found handlers.
    """
    deserialized = ejson.loads(data)
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
