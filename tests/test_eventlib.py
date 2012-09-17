from mock import Mock, patch

import eventlib
from eventlib import ejson, exceptions, conf


def test_parse_event_name():
    eventlib.parse_event_name('app.Event').should.be.equal(
        ('app.events', 'Event'))

    eventlib.parse_event_name.when.called_with('stuff').should.throw(
        exceptions.InvalidEventNameError,
        'The name "stuff" is invalid. Make sure you are using the '
        '"app.KlassName" format')

    eventlib.parse_event_name.when.called_with('other.stuff.blah').should.throw(
        exceptions.InvalidEventNameError,
        'The name "other.stuff.blah" is invalid. Make sure you are using the '
        '"app.KlassName" format')


@patch('eventlib.import_module')
def test_find_event(import_module):
    fake_module = Mock()
    fake_module.Event = 'my-lol-module'

    import_module.return_value = fake_module
    eventlib.find_event('app.Event').should.be.equals('my-lol-module')

    import_module.reset_mock()
    import_module.side_effect = ImportError
    eventlib.find_event.when.called_with('app.Event2').should.throw(
        exceptions.EventNotFoundError,
        'Event "app.Event2" not found. Make sure you have a class '
        'called "Event2" inside the "app.events" module.')


def test_handler_registry():
    eventlib.cleanup_handlers()

    @eventlib.handler('stuff.Klass')
    def do_nothing(data):
        return len(data)

    eventlib.HANDLER_REGISTRY.should.have.length_of(1)
    eventlib.HANDLER_REGISTRY['stuff.Klass'].should.be.equals([do_nothing])


def test_handler_with_methods():
    eventlib.cleanup_handlers()

    class MyEvent(eventlib.BaseEvent):

        @eventlib.handler
        def handle_stuff(self):
            pass

    eventlib.HANDLER_REGISTRY.should.have.length_of(1)
    eventlib.HANDLER_REGISTRY[MyEvent].should.be.equals([MyEvent.handle_stuff])


def test_handler_registry_cleanup():
    eventlib.cleanup_handlers()
    eventlib.HANDLER_REGISTRY.should.have.length_of(0)

    @eventlib.handler('stuff.Klass')
    def do_nothing(data):
        return -1

    @eventlib.handler('stuff.Blah')
    def do_another_nothing(data):
        return 0

    eventlib.HANDLER_REGISTRY.should.have.length_of(2)
    eventlib.HANDLER_REGISTRY['stuff.Klass'].should.be.equals([do_nothing])
    eventlib.HANDLER_REGISTRY['stuff.Blah'].should.be.equals([do_another_nothing])

    eventlib.cleanup_handlers('stuff.Klass')
    dict(eventlib.HANDLER_REGISTRY).should.be.equals(
        {'stuff.Blah': [do_another_nothing]})

    eventlib.cleanup_handlers()
    eventlib.HANDLER_REGISTRY.should.have.length_of(0)


@patch('eventlib.find_event')
def test_find_handlers(find_event):
    eventlib.cleanup_handlers()

    @eventlib.handler('app.Event')
    def stuff(data):
        return 0
    eventlib.find_handlers('app.Event').should.be.equals([stuff])

    @eventlib.handler('app.Event')
    def other_stuff(data):
        return 1
    eventlib.find_handlers('app.Event').should.be.equals([stuff, other_stuff])

    @eventlib.handler('app.Event2')
    def more_stuff(data):
        return 2
    eventlib.find_handlers('app.Event').should.be.equals([stuff, other_stuff])
    eventlib.find_handlers('app.Event2').should.be.equals([more_stuff])

    eventlib.find_handlers('dont.Exist').should.be.equal([])


@patch('eventlib.find_event')
def test_find_handlers_with_mixed_objects_and_strings(find_event):
    eventlib.cleanup_handlers()

    class MyEvent(eventlib.BaseEvent):
        @eventlib.handler
        def handle_stuff(self):
            pass

    find_event.return_value = MyEvent

    @eventlib.handler('stuff.MyEvent')
    def do_nothing(data):
        return len(data)

    eventlib.find_handlers('stuff.MyEvent').should.be.equals([
        MyEvent.handle_stuff, do_nothing
    ])


@patch('eventlib.datetime')
@patch('eventlib.process')
@patch('eventlib.find_event')
def test_log(find_event, process, datetime):
    eventlib.cleanup_handlers()
    datetime.now.return_value = 'tea time'

    event_cls = Mock()
    find_event.return_value = event_cls

    data = {'name': 'Event System', 'code': 42}
    eventlib.log('app.Event', data)
    find_event.assert_called_once_with('app.Event')
    event_cls.assert_called_once_with('app.Event', data)
    event_cls.return_value.validate.assert_called_once()
    process.assert_called_once_with('app.Event', ejson.dumps(data))


@patch('eventlib.datetime')
@patch('eventlib.process')
@patch('eventlib.find_event')
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


@patch('eventlib.find_event')
def test_process(find_event):
    eventlib.cleanup_handlers()

    handler = Mock()
    eventlib.handler('app.Event')(handler)

    handler2 = Mock()
    eventlib.handler('app.Event')(handler2)

    data = {'file': '/etc/passwd', 'server': 'yipster'}
    eventlib.process('app.Event', ejson.dumps(data))

    handler.assert_called_once_with(data)
    handler2.assert_called_once_with(data)


@patch('eventlib.find_event')
@patch('eventlib.logger')
def test_process_data_clean(logger, find_event):
    eventlib.cleanup_handlers()

    class MyEvent(eventlib.BaseEvent):
        def clean(self):
            raise exceptions.ValidationError('Owned!!11')

    data = {'name': 'Lincoln', 'answer': 42}
    find_event.return_value = MyEvent
    eventlib.process('stuff', ejson.dumps(data))
    logger.warning.assert_called_once_with(
        'The event system just got an exception while cleaning data '
        "for the event 'stuff'\n"
        "data: {\"answer\": 42, \"name\": \"Lincoln\"}\n"
        "exc: Owned!!11")


@patch('eventlib.find_event')
@patch('eventlib.logger')
def test_process_fails_gracefully(logger, find_event):
    eventlib.cleanup_handlers()
    conf.DEVELOPMENT = False

    handler_fail = Mock()
    handler_fail.side_effect = ValueError('P0wned!!!')
    eventlib.handler('myapp.CoolEvent')(handler_fail)

    handler = Mock()
    eventlib.handler('myapp.CoolEvent')(handler)

    data = {'a': 1}
    event = 'myapp.CoolEvent'
    eventlib.process(event, ejson.dumps(data))

    logger.warning.assert_called_once_with(
        'One of the handlers for the event "myapp.CoolEvent" has '
        'failed with the following exception: P0wned!!!')
    handler.assert_called_once_with(data)


def test_filter_data_values():
    eventlib.filter_data_values({'a': 'b', 'c': 'd'}).should.be.equals(
        {'a': 'b', 'c': 'd'}
    )
    eventlib.filter_data_values({'a': 'b', 'request': None}).should.be.equals(
        {'a': 'b'}
    )


@patch('eventlib.datetime')
@patch('eventlib.get_ip')
def test_get_default_values_with_request(get_ip, datetime):
    get_ip.return_value = '150.164.211.1'
    datetime.now.return_value = 'tea time!'
    data = {'foo': 'bar', 'request': Mock()}
    eventlib.get_default_values(data).should.be.equals({
        '__datetime__': 'tea time!',
        '__ip_address__': '150.164.211.1',
    })
