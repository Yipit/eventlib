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

import ejson
import eventlib
from mock import Mock, patch
from eventlib import core


@patch('eventlib.core.datetime')
@patch('eventlib.core.process')
@patch('eventlib.core.find_event')
@patch('eventlib.api.conf')
def test_log(conf, find_event, process, datetime):
    conf.getsetting.return_value = True
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
@patch('eventlib.api.conf')
def test_log_when_debug_is_false(conf, datetime, find_event, tasks):
    conf.getsetting.return_value = False
    core.cleanup_handlers()
    datetime.now.return_value = 'tea time'

    eventlib.log('app.Event')
    tasks.process_task.delay.assert_called_once_with('app.Event', ejson.dumps({
        '__ip_address__': '0.0.0.0', '__datetime__': 'tea time',
    }))


@patch('eventlib.core.datetime')
@patch('eventlib.core.process')
@patch('eventlib.core.find_event')
@patch('eventlib.api.conf')
def test_log_insert_datetime(conf, find_event, process, datetime):
    conf.getsetting.return_value = True
    datetime.now.return_value = 'tea time'
    data = {'name': 'Event System', 'code': 42}
    eventlib.log('app.Event', data)
    data['__datetime__'].should.be.equals('tea time')
