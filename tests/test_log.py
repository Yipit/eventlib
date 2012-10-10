from mock import Mock, patch

import eventlib
from eventlib import conf, core, ejson


@patch('eventlib.core.datetime')
@patch('eventlib.core.process')
@patch('eventlib.core.find_event')
def test_log(find_event, process, datetime):
    conf.DEBUG = True
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


@patch('eventlib.api.tasks')
@patch('eventlib.core.find_event')
@patch('eventlib.core.datetime')
def test_log_when_debug_is_false(datetime, find_event, tasks):
    conf.DEBUG = False
    core.cleanup_handlers()
    datetime.now.return_value = 'tea time'

    eventlib.log('app.Event')
    tasks.process_task.delay.assert_called_once_with('app.Event', ejson.dumps({
        '__ip_address__': '0.0.0.0', '__datetime__': 'tea time',
    }))


@patch('eventlib.core.datetime')
@patch('eventlib.core.process')
@patch('eventlib.core.find_event')
def test_log_insert_datetime(find_event, process, datetime):
    conf.DEBUG = True
    datetime.now.return_value = 'tea time'
    data = {'name': 'Event System', 'code': 42}
    eventlib.log('app.Event', data)
    data['__datetime__'].should.be.equals('tea time')
