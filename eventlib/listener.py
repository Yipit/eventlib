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

from eventlib.core import process_external, import_event_modules
from eventlib.ejson import loads
from eventlib.util import redis_connection


def listen_for_events():
    """Pubsub event listener

    Listen for events in the pubsub bus and calls the process function
    when somebody comes to play.
    """
    import_event_modules()
    conn = redis_connection.get_connection()
    pubsub = conn.pubsub()
    pubsub.subscribe("eventlib")
    for message in pubsub.listen():
        if message['type'] != 'message':
            continue
        data = loads(message["data"])
        if 'name' in data:
            event_name = data.pop('name')
            process_external(event_name, data)
