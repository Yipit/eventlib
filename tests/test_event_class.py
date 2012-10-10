from mock import patch

import eventlib
from eventlib import exceptions


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

channel_name = None
channel_data = None


@patch('eventlib.api.redis_connection')
def test_event_broadcast(redis_connection):
    class MyEvent(eventlib.BaseEvent):
        def broadcast(self, data):
            data['extra'] = 'extra_data'
            return data

    data = {'name': 'Lincoln', 'age': 25, 'answer': 42}
    event = MyEvent('stuff', data)

    event._broadcast()
    redis_connection.get_connection.return_value.publish.assert_called_once_with(
        'eventlib',
        '{"answer": 42, "age": 25, "name": "stuff", "extra": "extra_data"}',
    )
