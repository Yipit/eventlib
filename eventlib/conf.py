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

"""Holds a very thin wrapper to get default values for configuration
keys in the django settings system"""

from django.conf import settings


def getsetting(key, default=None):
    """Just a thin wrapper to avoid repeating code

    Also, this makes it easier to find places that are using
    configuration values and change them if we need in the future.
    """
    return getattr(settings, key, default)
