# Eventlib tutorial (p2)

This is the second step towards a deeper understanding of the
eventlib. The first one is just ["The basic usage of eventlib"](p1-tutorial.md).

In this small article, you'll learn in depth how to declare an event and
it's handlers.


## The event class

All the events must be available in the `app.events` module in your
Django app. This module can be either a `.py` file or a folder
containing an `__init__.py` file. If you choose the later option, make
sure that the event identifiers will be available in the initialization
file.

Also, event classes must inherit from the `eventlib.BaseEvent`
class. Just like this:

```python
# myproject/myapp/events.py

from eventlib import BaseEvent

class ProductViewedEvent(BaseEvent):
    pass
```

## The handlers

A handler is an action that will be taken as soon as a given event is
processed. Each event can have zero or more handlers. Although it's
useless, you can have an event that does not provide any handlers.

A handler can be either a method in the event class or a function
anywhere else in your codebase. To associate a handler to an event, you
must use the `eventlib.handler` decorator in this function or
method. Just like this:

```python
from myapp.models import ProductViewedModel
from eventlib import handler

@handler('myapp.ProductViewedEvent')
def log_to_mysql(data):
    ProductViewedModel.objects.create(user=data['user'])
```

Notice that the function based handler can be declared in any file in
your code base, not only in the `myapp/events.py` file. You just must
ensure that this file is loaded before processing the events.

Also, notice that you don't need to inform the event signature in the
decorator when you're using the class based approach.

```python
# myproject/myapp/events.py

from myapp.models import ProductViewedModel
from eventlib import BaseEvent, handler

class ProductViewedEvent(BaseEvent):
    @handler
    def log_to_mysql(self)
        ProductViewedModel.objects.create(user=self.data['user'])
```


## Validation

Eventlib also provides an easy way to validate data before processing
events. To add this layer, you just need to add the `clean` method to
your event class. Here is an example:

```python
# myproject/myapp/events.py

from eventlib import BaseEvent
from eventlib.exceptions import ValidationError

class ProductViewedEvent(BaseEvent):
    def clean(self):
        if not 'product' in self.data:
            raise ValidationError('You must inform a product')
        if self.data['user'].status != 'active':
            raise ValidationError(
                'Trying to log the activity of an inactive user')
```

As you can see, you can write your custom code to validate data sent to
the event. For the most common case, which is just verifying if some
keys are present, eventlib provides a method called `validate_keys`.
heck the following example to understand how it works:

```
class MyEvent(BaseEvent):
    def validate(self):
        self.validate_keys('user', 'product')
```

The `ValidationError` exception will be raised if one of the informed
keys is missing from the `self.data` dictionary.

### Be careful with validation operations

The validation happens **before** sending the data to the *celery*
workers, so it is not a good idea to add expensive operations in this
side, cause they will be processed in the same place your main code is
running.

## Going further

This is the second part of the eventlib tutorial. The next part is the
["Asynchronous logging"](docs/p3-asynchronous-logging.md) article.
