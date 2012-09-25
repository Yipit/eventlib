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

"""This file holds all serializers needed by the event library to
exchange data through sqs (actually, for any other backend that needs
that).
"""

from . import ejson
from datetime import datetime
from dateutil import parser


@ejson.register_serializer(datetime)
def serialize_datetime(instance):
    """Returns a string representation of a datetime instance"""
    return instance.isoformat()


@ejson.register_deserializer(datetime)
def deserialize_datetime(data):
    """Return a datetime instance based on the values of the data param"""
    return parser.parse(data)
