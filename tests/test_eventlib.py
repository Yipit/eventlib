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
import os
from mock import Mock, patch, call

import eventlib
from eventlib import ejson, exceptions, conf, core, tasks


def test_parse_event_name():
    core.parse_event_name('app.Event').should.be.equal(
        ('app.events', 'Event'))

    core.parse_event_name.when.called_with('stuff').should.throw(
        exceptions.InvalidEventNameError,
        'The name "stuff" is invalid. Make sure you are using the '
        '"app.KlassName" format')

    core.parse_event_name.when.called_with('other.stuff.blah').should.throw(
        exceptions.InvalidEventNameError,
        'The name "other.stuff.blah" is invalid. Make sure you are using the '
        '"app.KlassName" format')


@patch('eventlib.core.import_module')
def test_find_event(import_module):
    fake_module = Mock()
    fake_module.Event = 'my-lol-module'

    import_module.return_value = fake_module
    core.find_event('app.Event').should.be.equals('my-lol-module')

    import_module.reset_mock()
    import_module.side_effect = ImportError
    core.find_event.when.called_with('app.Event2').should.throw(
        exceptions.EventNotFoundError,
        'Event "app.Event2" not found. Make sure you have a class '
        'called "Event2" inside the "app.events" module.')


def test_handler_registry():
    core.cleanup_handlers()

    @eventlib.handler('stuff.Klass')
    def do_nothing(data):
        return len(data)

    core.HANDLER_REGISTRY.should.have.length_of(1)
    core.HANDLER_REGISTRY['stuff.Klass'].should.be.equals([do_nothing])


def test_handler_with_methods():
    core.cleanup_handlers()

    class MyEvent(eventlib.BaseEvent):

        @eventlib.handler
        def handle_stuff(self):
            pass

    core.HANDLER_REGISTRY.should.have.length_of(1)
    core.HANDLER_REGISTRY[MyEvent].should.be.equals([MyEvent.handle_stuff])


def test_handler_registry_cleanup():
    core.cleanup_handlers()
    core.HANDLER_REGISTRY.should.have.length_of(0)

    @eventlib.handler('stuff.Klass')
    def do_nothing(data):
        return -1

    @eventlib.handler('stuff.Blah')
    def do_another_nothing(data):
        return 0

    core.HANDLER_REGISTRY.should.have.length_of(2)
    core.HANDLER_REGISTRY['stuff.Klass'].should.be.equals([do_nothing])
    core.HANDLER_REGISTRY['stuff.Blah'].should.be.equals([do_another_nothing])

    core.cleanup_handlers('stuff.Klass')
    dict(core.HANDLER_REGISTRY).should.be.equals(
        {'stuff.Blah': [do_another_nothing]})

    core.cleanup_handlers()
    core.HANDLER_REGISTRY.should.have.length_of(0)


@patch('eventlib.core.find_event')
def test_find_handlers(find_event):
    core.cleanup_handlers()

    @eventlib.handler('app.Event')
    def stuff(data):
        return 0
    core.find_handlers('app.Event').should.be.equals([stuff])

    @eventlib.handler('app.Event')
    def other_stuff(data):
        return 1
    core.find_handlers('app.Event').should.be.equals([stuff, other_stuff])

    @eventlib.handler('app.Event2')
    def more_stuff(data):
        return 2
    core.find_handlers('app.Event').should.be.equals([stuff, other_stuff])
    core.find_handlers('app.Event2').should.be.equals([more_stuff])

    core.find_handlers('dont.Exist').should.be.equal([])


@patch('eventlib.core.find_event')
def test_find_handlers_with_mixed_objects_and_strings(find_event):
    core.cleanup_handlers()

    class MyEvent(eventlib.BaseEvent):
        @eventlib.handler
        def handle_stuff(self):
            pass

    find_event.return_value = MyEvent

    @eventlib.handler('stuff.MyEvent')
    def do_nothing(data):
        return len(data)

    core.find_handlers('stuff.MyEvent').should.be.equals([
        MyEvent.handle_stuff, do_nothing
    ])


@patch('eventlib.core.datetime')
@patch('eventlib.core.process')
@patch('eventlib.core.find_event')
def test_log(find_event, process, datetime):
    core.cleanup_handlers()
    datetime.now.return_value = 'tea time'

    event_cls = Mock()
    find_event.return_value = event_cls

    data = {'name': 'Event System', 'code': 42}
    eventlib.log('app.Event', data)
    find_event.assert_called_once_with('app.Event')
    event_cls.assert_called_once_with('app.Event', data)
    event_cls.return_value.validate.assert_called_once()
    process.assert_called_once_with('app.Event', ejson.dumps(data))


@patch('eventlib.core.datetime')
@patch('eventlib.core.process')
@patch('eventlib.core.find_event')
def test_log_insert_datetime(find_event, process, datetime):
    datetime.now.return_value = 'tea time'
    data = {'name': 'Event System', 'code': 42}
    eventlib.log('app.Event', data)
    data['__datetime__'].should.be.equals('tea time')


def test_event_validate():
    class MyEvent(eventlib.BaseEvent):
        pass

    data = {'name': 'Lincoln', 'age': 25, 'answer': 42}
    event = MyEvent('stuff', data)

    assert event.validate_keys('name', 'age')

    event.validate_keys.when.called_with('unknown', 'blah').should.throw(
        exceptions.ValidationError,
        'One of the following keys are missing from the event\'s data: '
        'unknown, blah')


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
def test_process_fails_gracefully(logger, find_event):
    core.cleanup_handlers()
    conf.DEBUG = False

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
def test_process_raises_the_exception_when_debugging(find_event):
    core.cleanup_handlers()
    conf.DEBUG = True

    handler_fail = Mock()
    handler_fail.side_effect = ValueError('P0wned!!!')
    eventlib.handler('myapp.CoolEvent')(handler_fail)
    name, data = 'myapp.CoolEvent', ejson.dumps({'a': 1})
    core.process.when.called_with(name, data).should.throw(
        ValueError, 'P0wned!!!')


def test_filter_data_values():
    core.filter_data_values({'a': 'b', 'c': 'd'}).should.be.equals(
        {'a': 'b', 'c': 'd'}
    )
    core.filter_data_values({'a': 'b', 'request': None}).should.be.equals(
        {'a': 'b'}
    )


@patch('eventlib.core.datetime')
@patch('eventlib.core.get_ip')
def test_get_default_values_with_request(get_ip, datetime):
    get_ip.return_value = '150.164.211.1'
    datetime.now.return_value = 'tea time!'
    data = {'foo': 'bar', 'request': Mock()}
    core.get_default_values(data).should.be.equals({
        '__datetime__': 'tea time!',
        '__ip_address__': '150.164.211.1',
    })


@patch('eventlib.tasks.process')
def test_celery_process_wrapper(process):
    tasks.process_task('name', 'data')
    process.assert_called_once_with('name', 'data')


@patch('django.conf.importlib')
def test_django_integration(importlib):
    # Given I mock django conf
    settings = importlib.import_module.return_value
    settings.LOCAL_GEOLOCATION_IP = 'CHUCK NORRIS'

    # When I reload the eventlib conf with the django environment
    # variable
    os.environ['DJANGO_SETTINGS_MODULE'] = 'LOL'
    reload(conf)

    # Then it should contain the mocked values
    conf.LOCAL_GEOLOCATION_IP.should.equal('CHUCK NORRIS')
