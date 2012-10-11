from mock import call, patch

from eventlib import ejson
from eventlib.listener import listen_for_events


def gen():
    for i in range(2):
        test_data = ejson.dumps({'name': 'app.TestEvent', 'a': 'b'})
        yield {'type': 'message', 'data': test_data}


@patch('eventlib.listener.redis_connection')
@patch('eventlib.listener.process_external')
@patch('eventlib.conf.settings')
def test_read_events(settings, process_external, redis_connection):
    pubsub = redis_connection.get_connection.return_value.pubsub
    pubsub.return_value.listen.side_effect = gen
    listen_for_events()

    process_external.assert_has_calls([
        call(u'app.TestEvent', {'a': 'b'}),
        call(u'app.TestEvent', {'a': 'b'}),
    ])
