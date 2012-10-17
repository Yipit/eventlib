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

"""This file implements the public interface of our event tracker lib"""

from . import ejson
from . import conf
from . import core
from . import tasks
from .exceptions import ValidationError
from .util import redis_connection


def _register_handler(event, fun, external=False):
    """Register a function to be an event handler"""
    registry = core.HANDLER_REGISTRY
    if external:
        registry = core.EXTERNAL_HANDLER_REGISTRY

    if event in registry:
        registry[event].append(fun)
    else:
        registry[event] = [fun]
    return fun


class MetaEvent(type):
    """Takes care of the methods marked as handlers in an Event class"""

    def __new__(mcs, name, bases, attrs):
        newcls = type.__new__(mcs, name, bases, attrs)

        # Collecting the methods that were registered as handlers for
        # the class that we're processing right now.
        registered = \
            [m for m in attrs.items() if m[1] in core.HANDLER_METHOD_REGISTRY]

        # Just registering the method as a handler for the current class
        for method_name, func in registered:
            core.HANDLER_METHOD_REGISTRY.remove(func)
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

    def _broadcast(self):
        data = self.broadcast(self.data)
        client = redis_connection.get_connection()
        if client:
            # If not redis client, don't broadcast
            data['name'] = self.name
            data = ejson.dumps(data)
            client.publish("eventlib", data)

    def broadcast(self, data):
        """Returns all the data that will be passed to the external handlers

        Override this method and update the `data` dictionary to provide
        all the data that you want to pass to external handlers.
        """
        return data


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
        core.HANDLER_METHOD_REGISTRY.append(param)
        return param


def external_handler(param):
    return lambda f: _register_handler(param, f, external=True)


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
    data.update(core.get_default_values(data))

    # InvalidEventNameError, EventNotFoundError
    event_cls = core.find_event(name)
    event = event_cls(name, data)
    event.validate()                # ValidationError
    data = core.filter_data_values(data)
    data = ejson.dumps(data)        # TypeError

    # We don't use celery when developing
    if conf.getsetting('DEBUG'):
        core.process(name, data)
    else:
        tasks.process_task.delay(name, data)
