"""Holds all exceptions used in the loglib api"""


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
