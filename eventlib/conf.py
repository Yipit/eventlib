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

"""Holds configuration values for the eventlib"""

import os

DEBUG = True

LOCAL_GEOLOCATION_IP = ''


# Django compatibility layer

if 'DJANGO_SETTINGS_MODULE' in os.environ:
    from django.conf import settings

    DEBUG = getattr(settings, "DEBUG", DEBUG)
    LOCAL_GEOLOCATION_IP = getattr(
        settings, "LOCAL_GEOLOCATION_IP", LOCAL_GEOLOCATION_IP)
