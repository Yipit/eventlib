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

import redis
from .conf import getsetting


UNKNOWN_IP = '0.0.0.0'


def get_ip(request):
    """Return the IP address inside the HTTP_X_FORWARDED_FOR var inside
    the `request` object.

    The return of this function can be overrided by the
    `LOCAL_GEOLOCATION_IP` variable in the `conf` module.

    This function will skip local IPs (starting with 10. and equals to
    127.0.0.1).
    """
    if getsetting('LOCAL_GEOLOCATION_IP'):
        return getsetting('LOCAL_GEOLOCATION_IP')

    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if not forwarded_for:
        return UNKNOWN_IP

    for ip in forwarded_for.split(','):
        ip = ip.strip()
        if not ip.startswith('10.') and not ip == '127.0.0.1':
            return ip

    return UNKNOWN_IP


class ConnectionManager(object):
    """Helper redis connector"""

    conn = None

    def get_connection(self):
        """Return a valid redis connection based on the following settings

          * `REDIS_CONNECTIONS`
          * `EVENTLIB_REDIS_CONFIG_NAME`

        The first one is a dictionary in the following format:

          >>> {
          ...   'server1': {'HOST': 'redis-server-1', 'POST': 9001},
          ...   'server2': {'HOST': 'redis-server-2', 'POST': 9002},
          ... ]

        The second one is the name of the entry present in the above
        dict, like `server1` or `server2`.
        """

        if self.conn:
            return self.conn

        redis_configs = getsetting('REDIS_CONNECTIONS')
        if redis_configs:
            config_name = getsetting('EVENTLIB_REDIS_CONFIG_NAME', 'default')
            config = redis_configs[config_name]
            host = config['HOST']
            port = config['PORT']
            self.conn = redis.StrictRedis(host=host, port=port)
        else:
            self.conn = None
        return self.conn

redis_connection = ConnectionManager()
