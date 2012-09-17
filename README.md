# Event API spec

This is an attempt to specify a generic, but flexible way to log events
in our codebase. There are two public APIs.

## Public api

### Recording events

In order to log an event, you need two things: the event name and the
data that it expects. Here's an example:

```python
# steadymark: ignore
>>> from eventlib import log
>>> log('app.EventName', {'username': 'test guy'})
```

The event name above contains two very important pieces of information
about the event: the app and the class name that inherits from
`BaseEvent`. It is _required_ to declare your events in a module called
`events` inside the app folder. We will go deeper into it in the next
section.

If, by any chance, you try to access an event that does not exist, a
custom exception should be raised, stating exactly what happened:

```python
>>> # inside the event/log.py
>>> class EventNotFound(Exception):
...     pass
...
>>> def _get_event(name):
...     app, event_name = _parse_event_name(name)
...     if name not in get_events():
...         raise EventNotFound(
...             'There is no event named {} in the {} app'.format(
...                 event_name, app
...             )
...         )
```

### Declaring an event

This is a three step process.

 1. Declare an event object
 1. Optionally provide a component to validate the data received by this
    event.
 1. Describe the handlers.

 So, we end up with something like this:
<pre>
         -------------
        | event class |
         -------------
               |
              / \
      optional   handlers
     validator
</pre>

Declaring an event should be as simple as the following example:

```python
>>> from eventlib import BaseEvent
>>> class DealClick(BaseEvent):
...     pass
```

This is the only required step to declare an event. But, our event won't
go anywhere without `handlers`. We use them to declare the actions that
the event will actually trigger. Writing to a database, making an http
call or executing a celery task are some examples of actions that can be
declared in a handler.

The first way to add a handler to an event is by adding a decorated
method to your event class. Like this:

```python
>>> import eventlib
>>> class EmailClick(eventlib.BaseEvent):
...     @eventlib.handler
...     def increment_redis_key(self):
...         key = 'deal:{}:clicks'.format(self.data.get('key'))
...         self.redis(key).incr()
...
...     @eventlib.handler
...     def save_to_mysql(self):
...         data = self.data.copy()
...         data.pop('unused_key')
...         self.mysql('apps.EmailClick').save(**data)
...
>>> eventlib.HANDLER_REGISTRY[EmailClick]
[<unbound method EmailClick.save_to_mysql>, <unbound method EmailClick.increment_redis_key>]
```

But if you are in a scenario where functions will fit your needs better,
like when you need to declare a handler in another module, you can do
something like this:

```python
>>> import eventlib
>>>
>>> @eventlib.handler('api.ApiCall')
... def call_3rd_party_api(event):
...     api_key = event.data('api_key')
...     res = requests.get(settings.THIRDPARTYAPI_URL.format(api_key))
...     User.objects.filter(email=res.content).update(discount=99)
```

Please notice that handlers declared as methods will always be called
*before* the function based handlers.

### Data validation

Events are added to a queue before being processed. It's a long road
from calling the `log()` function to actually using the data passed to
it. So, instead of allowing the log processor to start all the steps of
serialization, sending, deserialization and so on, this API provides a
way to validate the data that the log expects. This validation will be
called when the task runs. Here's the way to validate your event's data:

```python
>>> import eventlib
>>> class MyEvent(eventlib.BaseEvent):
...     def clean(self):
...         required_keys = 'deal_id', 'user_id', 'code'
...         missing_keys = []
...         for key in required_keys:
...             if not key in self.data:
...                 missing_keys.append(key)
...         if missing_keys:
...             raise eventlib.ValidationError(
...                 'The following keys are missing: {}'.format(
...                     ', '.join(missing_keys)))
```

There's also a helper for this very common case:

```python
>>> def clean(self):
...    # This call will raise the ValidationError if any of these
...    # keys are missing
...    self.require_data_keys(['deal_id', 'user_id', 'code'])
```

Behind the scenes, things are something like this:

```python
>>> def log(name, data):
...     event = special_import(name)()
...     try:
...         data = event.clean(data)
...     except ValidationError:
...         log_to_sentry.error("Invalid Data Passed to blah from foo")
...     else:
...         delay_event(event, data)
```

## Params that events can take

Events can take any kind of parameter serializable by the `json.dumps`
function. If you are willing to pass parameters that are not supported
by this library by default, you will need to refer to the
[extensible-serialization](docs/extensible-serialization.md) document.

## Events are not immediately processed

As we don't want to compromise the performance of our main application
with something secondary like logging, this spec also demands that all
logging should run in separate tasks dispatched through celery.

The flow is like this:

<pre>
     ---------------------
    | eventlib.log() call |
     ---------------------
         \ -----------------
          | serialize(data) |
           -----------------
                \ ----------------------
                 | log_processing.delay |
                / ----------------------
           -------------------
          | deserialize(data) |
         / -------------------
     ------------------------
    | eventlib.process(data) |
     ------------------------
</pre>

### Handlers should fail gracefully

There can be a list of different handlers to execute in the same event
processing and we must ensure that if one of these handlers fail, the
other ones will have their chance to try. This way, the `process()`
functions should iterate over all registered handlers for that event
taking care to handle any error _and_ log it with the default python
`logging` module. Something like this:

```
>>> handlers = self.registered_handlers()
... for h in handlers:
...     try:
...         h(deserialized_data)
...     except:
...         log_to_sentry()
```

## JavaScript API

If you are a front end developer and are afraid that you would be out of
the new event sensation, don't worry! We've got JavaScript

There's an HTTP view that wraps the `event.log()` call. On top of this
function, we have the `yipit.event.log()` JS function that works exactly
like the python version.

Behind this JavaScript call, there's an ajax call in the following
format:

    POST /event/log?__event__=app.EventName&param1=val1&param2=val2

The view will parse the query string and build something like this:

```python
>>> event_name = 'app.EventName'
>>> data = {'param1': 'val1', 'param2': 'val2'}
```
