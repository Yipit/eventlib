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

import sure
_ = sure
from eventlib import ejson
from datetime import datetime
from mock import Mock, patch


class Person(object):
    """Small class that will help us to test the ejson library
    """
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return u'Person("{}", {})'.format(self.name, self.age)


def test_register_serializer():
    # Making sure we have a clear registry before writing stuff to it
    ejson.cleanup_registry()
    dict(ejson.REGISTRY).should.be.equal({})

    # Registering our first serializer for a custom object
    @ejson.register_serializer(Person)
    def serialize_person(instance):
        return {
            'name': instance.name,
            'age': instance.age,
        }
    ejson.REGISTRY.should.have.length_of(1)
    ejson.REGISTRY[Person].should.be.equal(serialize_person)

    # Testing the serializer registry with the python data type
    @ejson.register_serializer(datetime)
    def serialize_datetime(instance):
        return instance.isoformat()
    ejson.REGISTRY.should.have.length_of(2)
    ejson.REGISTRY[datetime].should.be.equal(serialize_datetime)

    # Now, testing the cleanup_registry function for real
    ejson.cleanup_registry()
    dict(ejson.REGISTRY).should.be.equal({})


def test_serialization_with_datetime():
    ejson.cleanup_registry()
    value = {'dt': datetime(2012, 8, 22, 3, 44, 05)}

    # Before registering
    ejson.dumps.when.called_with(value).should.throw(
        TypeError,
        'datetime.datetime(2012, 8, 22, 3, 44, 5) is not JSON serializable')

    # After registering
    @ejson.register_serializer(datetime)
    def serialize_datetime(instance):
        return instance.isoformat()
    ejson.dumps(value).should.be.equals(
        '{"dt": {"__class__": "datetime.datetime", "__value__": "2012-08-22T03:44:05"}}')


def test_serialization_with_custom_object():
    ejson.cleanup_registry()
    value = Person('Lincoln', 25)

    # Before registering
    ejson.dumps.when.called_with(value).should.throw(
        TypeError, 'Person("Lincoln", 25) is not JSON serializable')

    # After registering
    @ejson.register_serializer(Person)
    def serialize_person(instance):
        return {"name": instance.name, "age": instance.age}
    ejson.dumps(value).should.be.equals(
        '{"__class__": "tests.test_ejson.Person", "__value__": {"age": 25, "name": "Lincoln"}}')


def test_deserialization_registry():
    ejson.cleanup_deserialization_registry()
    dict(ejson.DESERIALIZE_REGISTRY).should.be.equal({})

    @ejson.register_deserializer(Person)
    def deserialize_person(data):
        return Person(data['name'], data['age'])

    ejson.DESERIALIZE_REGISTRY.should.have.length_of(1)
    ejson.DESERIALIZE_REGISTRY[Person].should.be.equal(deserialize_person)

    # Testing the cleanup for real
    ejson.cleanup_deserialization_registry()
    ejson.DESERIALIZE_REGISTRY.should.have.length_of(0)


def test_deserialization():
    ejson.cleanup_deserialization_registry()

    @ejson.register_deserializer(Person)
    def deserialize_person(data):
        return Person(data['name'], data['age'])

    obj = ejson.loads('{"age": 25, "name": "Lincoln"}')
    person = ejson.deserialize(Person, obj)
    person.should.be.a(Person)
    person.name.should.be.equals('Lincoln')
    person.age.should.be.equals(25)


def test_auto_deserialization():
    ejson.cleanup_deserialization_registry()

    @ejson.register_deserializer(Person)
    def deserialize_person(data):
        return Person(data['name'], data['age'])

    person = ejson.loads(
        '{"__class__": "tests.test_ejson.Person", "__value__": {"age": 25, "name": "Lincoln"}}')
    person.should.be.a(Person)
    person.name.should.be.equals('Lincoln')
    person.age.should.be.equals(25)


def test_deserialization_with_no_objects_registered():
    ejson.cleanup_deserialization_registry()
    obj = ejson.loads('{"age": 25, "name": "Lincoln"}')
    ejson.deserialize.when.called_with(Person, obj).should.throw(
        TypeError,
        "There is no deserializer registered to handle instances of 'Person'")


@patch('eventlib.ejson.import_module')
@patch('eventlib.ejson.deserialize')
def test_internal_convert_from(deserialize, import_module):
    (u'Making sure that the _convert_from function can find the right '
     u'module/class described by the dotted notation in the "__class__" key')

    mymodule = Mock()
    mymodule.MyClass = Mock()
    import_module.return_value = mymodule
    deserialize.return_value = 'Awesome!'

    converted = ejson._convert_from(
        {'__class__': 'mymodule.MyClass', '__value__': {'name': 'Neil A.'}})

    import_module.assert_called_once_with('mymodule')
    converted.should.be.equals('Awesome!')
    deserialize.assert_called_once_with(
        mymodule.MyClass, {'name': 'Neil A.'})


@patch('eventlib.ejson.import_module')
@patch('eventlib.ejson.deserialize')
def test_internal_convert_from_with_normal_values(deserialize, import_module):
    (u'Making sure that the _convert_from function can handle values without '
     u'the __class__/__value__ special keys')

    mymodule = Mock()
    mymodule.MyClass = Mock()
    import_module.side_effect = KeyError('Owned')

    converted = ejson._convert_from({'name': 'Yuri G.'})
    converted.should.be.equal({'name': 'Yuri G.'})
