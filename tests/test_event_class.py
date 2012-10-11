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


@patch('eventlib.api.redis_connection')
def test_event_default_broadcast(conn):

    # Given I declare a new event
    class CoolEvent(eventlib.BaseEvent):
        pass

    # When I create my event with some data
    data = {'developer': 'Steve', 'skills': 'a lot!'}
    event = CoolEvent('stuff', data)

    # Then the default broadcast function should return the same data
    # that was informed before
    event.broadcast(data).should.equal(data)
