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

from mock import Mock, patch

import eventlib
from eventlib import core, ejson, exceptions


@patch('eventlib.core.find_event')
def test_process(find_event):
    core.cleanup_handlers()

    handler = Mock()
    eventlib.handler('app.Event')(handler)

    handler2 = Mock()
    eventlib.handler('app.Event')(handler2)

    data = {'file': '/etc/passwd', 'server': 'yipster'}
    core.process('app.Event', ejson.dumps(data))

    handler.assert_called_once_with(data)
    handler2.assert_called_once_with(data)


@patch('eventlib.core.find_event')
def test_process_external(find_event):
    core.cleanup_handlers()

    handler = Mock()
    eventlib.external_handler('app.Event')(handler)

    data = {'file': '/etc/passwd', 'server': 'yipster'}
    core.process_external('app.Event', ejson.dumps(data))

    handler.assert_called_once_with(data)


@patch('eventlib.core.find_event')
@patch('eventlib.core.logger')
def test_process_data_clean(logger, find_event):
    core.cleanup_handlers()

    class MyEvent(eventlib.BaseEvent):
        def clean(self):
            raise exceptions.ValidationError('Owned!!11')

    data = {'name': 'Lincoln', 'answer': 42}
    find_event.return_value = MyEvent
    core.process('stuff', ejson.dumps(data))
    logger.warning.assert_called_once_with(
        'The event system just got an exception while cleaning data '
        "for the event 'stuff'\n"
        "data: {\"answer\": 42, \"name\": \"Lincoln\"}\n"
        "exc: Owned!!11")


@patch('eventlib.core.find_event')
@patch('eventlib.core.logger')
@patch('eventlib.conf.settings')
def test_process_fails_gracefully(settings, logger, find_event):
    core.cleanup_handlers()
    settings.DEBUG = False

    handler_fail = Mock()
    handler_fail.side_effect = ValueError('P0wned!!!')
    eventlib.handler('myapp.CoolEvent')(handler_fail)

    handler = Mock()
    eventlib.handler('myapp.CoolEvent')(handler)

    data = {'a': 1}
    event = 'myapp.CoolEvent'
    core.process(event, ejson.dumps(data))

    logger.warning.assert_called_once_with(
        'One of the handlers for the event "myapp.CoolEvent" has '
        'failed with the following exception: P0wned!!!')
    handler.assert_called_once_with(data)


@patch('eventlib.core.find_event')
@patch('eventlib.core.logger')
@patch('eventlib.conf.settings')
def test_process_external_fails_gracefully(settings, logger, find_event):
    core.cleanup_handlers()
    settings.DEBUG = False

    handler_fail = Mock()
    handler_fail.side_effect = ValueError('P0wned!!!')
    eventlib.external_handler('myapp.CoolEvent')(handler_fail)

    handler = Mock()
    eventlib.external_handler('myapp.CoolEvent')(handler)

    data = {'a': 1}
    event = 'myapp.CoolEvent'
    core.process_external(event, ejson.dumps(data))

    logger.warning.assert_called_once_with(
        'One of the handlers for the event "myapp.CoolEvent" has '
        'failed with the following exception: P0wned!!!')
    handler.assert_called_once_with(data)


@patch('eventlib.core.find_event')
@patch('eventlib.conf.settings')
def test_process_raises_the_exception_when_debugging(settings, find_event):
    core.cleanup_handlers()
    settings.DEBUG = True

    handler_fail = Mock()
    handler_fail.side_effect = ValueError('P0wned!!!')
    eventlib.handler('myapp.CoolEvent')(handler_fail)
    name, data = 'myapp.CoolEvent', ejson.dumps({'a': 1})
    core.process.when.called_with(name, data).should.throw(
        ValueError, 'P0wned!!!')


@patch('eventlib.core.find_event')
@patch('eventlib.conf.settings')
def test_process_external_raises_the_exception_when_debugging(
        settings, find_event):
    core.cleanup_handlers()
    settings.DEBUG = True

    handler_fail = Mock()
    handler_fail.side_effect = ValueError('P0wned!!!')
    eventlib.external_handler('myapp.CoolEvent')(handler_fail)
    name, data = 'myapp.CoolEvent', ejson.dumps({'a': 1})
    core.process_external.when.called_with(name, data).should.throw(
        ValueError, 'P0wned!!!')
