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
