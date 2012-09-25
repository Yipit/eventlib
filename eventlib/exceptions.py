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

"""Holds all exceptions used in the eventlib api"""


__all__ = (
    'ValidationError', 'EventNotFoundError', 'InvalidEventNameError',
)


class InvalidEventNameError(Exception):
    """Raised when an invalid event is being parsed"""


class EventNotFoundError(Exception):
    """Exception raised when an event name can't be resolved"""


class ValidationError(Exception):
    """Raised when a problem with data passed to an event class is found
    """
