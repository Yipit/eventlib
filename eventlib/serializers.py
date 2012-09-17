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
