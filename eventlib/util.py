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

from . import conf

UNKNOWN_IP = '0.0.0.0'


def get_ip(request):
    """Return the IP address inside the HTTP_X_FORWARDED_FOR var inside
    the `request` object.

    The return of this function can be overrided by the
    `LOCAL_GEOLOCATION_IP` variable in the `conf` module.

    This function will skip local IPs (starting with 10. and equals to
    127.0.0.1).
    """
    if conf.LOCAL_GEOLOCATION_IP:
        return conf.LOCAL_GEOLOCATION_IP

    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if not forwarded_for:
        return UNKNOWN_IP

    for ip in forwarded_for.split(','):
        ip = ip.strip()
        if not ip.startswith('10.') and not ip == '127.0.0.1':
            return ip

    return UNKNOWN_IP
