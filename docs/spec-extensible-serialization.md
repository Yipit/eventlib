# Extensible serialization spec

There are countless scenarios that we need to exchange data between
different systems, implemented in different languages and technologies.
Even in the same system, when implementing data exchange between the
backend and the frontend we face the need to convert the language data
types to another format and then do the oposite when the data arrives in
the other side of the wire.

A very simple and flexible format that seems to fit most of our needs is
the JavaScript Object Notation, or simple `json`. It is very hard to
find a programming language these days that does not support it, even
the low level ones, like C, C++, etc.

Json is enough when we need to exchange data types like integers,
doubles, strings, lists and hash tables. The problem starts when we need
to exchange a complex data type. And it's the exact aim of this
document: providing an API to extend the `json` library to make it easy
to register new serializers and new deserializers.

## How to identify a data type

Before talking about how to serialize or deserialize a data type, it is
important to know how we identify the type of a complex python
object. Let's start with the basic ones. The number `1` is just an
instance of the built-in class `int`. The literal `"stuff"` is
translated to something like `str("stuff")` and is an instance of the
`str` class. Lists and dictionaries are the same:

```python
mylist = [1, 2, 3]
isinstance(mylist, list) # Yeah, it's an instance of the list class
mydict = {"a": 1, "b": 2}
isinstance(mydict, dict) # Also, it's an instance of the dict class
```

But what about a home made class? Like this this one:

```python
class A(object):
    def __init__(self):
        self.myint = 42
        self.mystr = "nothing special"
        self.mylist = [self.myint, self.mystr]
```

As we know, python classes are *also* python *types*. So, if you create
a new instance of `A()`, let's say, like this: `a = A()`. You can say
that the type of the `a` variable is `A`, just like the type of `1` is
`int`. In other words, the built-in function `isinstance()` will tell
you if an instance type is equals to a given type/class.

## What the json library knows about types

So, the `json` module knows how to deal with these built-in types, but
it does not understand the complex types. Have you tried to dump a
`datetime.datetime` instance with the `json` library? Here's what you
get:

```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  (...)
  File ".../encoder.py"
    raise TypeError(repr(o) + " is not JSON serializable")
TypeError: datetime.datetime(2012, 8, 22, 12, 19, 12, 577078) is not JSON serializable
```

It happens because the `json` library doesn't know how to deal with
these objects. A simple fix would be doing something like this:

```python
>>> import json
>>> def converter(val):
...     if isinstance(val, datetime):
...         return val.isoformat()
...     raise TypeError
...
>>> date = datetime(2012, 8, 22, 12, 23)
>>> json.dumps({'a': 'b', 'b': date}, default=converter)
'{"a": "b", "b": "2012-08-22T12:23:00"}'
```

## How to extend the json library in an elegant way

Instead of creating a module with all the types that you are willing to
support in your system, this spec suggests the introduction of an API
that register types and their handlers.

It is a two step process. First, let's declare a complex type called
`Person`. The second step consists in letting the `ejson` library know
how to serialize objects of that class. To do that, you need to
register a serializer. Take a look at the full example:

```python
>>> class Person(object):
...     def __init__(self, name, age, gender):
...        self.name = name
...        self.age = age
...        self.gender = gender
...
>>> from ylib import ejson
>>> @ejson.register_serializer(Person)
... def serialize_person(instance):
...     return {
...         'name': instance.name,
...         'age': instance.age,
...         'gender': instance.gender,
...     }
...
>>> from ylib.ejson import dumps
>>> dumps(Person('Lincoln', 25, 'male'))
'{"__class__": "steadymark.core.Person", "__value__": {"gender": "male", "age": 25, "name": "Lincoln"}}'
```

### One more step serializing complex objects

In order to find the right deserializer for a given value, we also add
the dotted class dotted path to the `json` info returned by our custom
`dumps()` function.

Notice that we also save the module where the class was declared, to
avoid namespace collision.

## Deserializing objects is a little bit harder

In the last example, we've serialized an instance of the `Person` class
with the help of the registered serializer. But, what happens if we need
to deserialize that object after receiving its json description from the
wire?

It is not simple to guess that a dictionary with the "name", "age" and
"gender" keys is a `Person` instance. To make it a bit easier to handle
this scenario, this spec suggests the introduction of a registry of
deserializers and an easy way to retrieve them. Thus, if you are writing
a component that needs to handle a field that you are sure that
represents a `Person`, you can do something like this:

```python
>>> from ylib import ejson
>>> import json
>>>
>>> class Person(object):
...     def __init__(self, name, age, gender):
...        self.name = name
...        self.age = age
...        self.gender = gender
...
>>> @ejson.register_deserializer(Person)
... def deserialize_person(data):
...     return Person(data['name'], data['age'], data['gender'])
...
>>>
>>> from ylib import ejson
>>> content = '{"gender": "male", "age": 25, "name": "Lincoln"}'
>>> obj = json.loads(content)
>>> person = ejson.deserialize(Person, obj)
>>> isinstance(person, Person)
True
```

### Automating deserialization

The `json.loads` function is not aware of our special parameter
`__class__`, so we also provide a wrapper for it, called `ejson.loads`.
Writing code to deserialize objects that were serialized by the `ejson`
library should be as simple as this following example:

```
from ylib import ejson
from yourapp.person import Person
person = ejson.loads(http_response.content)
isinstance(person, Person) == True
```
