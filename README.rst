============
dictionaries
============

Python dictionary implementations
"""""""""""""""""""""""""""""""""


.. image:: https://img.shields.io/travis/pasztorpisti/py-dictionaries.svg?style=flat
    :target: https://travis-ci.org/pasztorpisti/py-dictionaries
    :alt: build

.. image:: https://img.shields.io/codacy/grade/9920e31609734de8815aa995b70b96e7/master.svg?style=flat
    :target: https://www.codacy.com/app/pasztorpisti/py-dictionaries
    :alt: code quality

.. image:: https://img.shields.io/coveralls/pasztorpisti/py-dictionaries/master.svg?style=flat
    :target: https://coveralls.io/r/pasztorpisti/py-dictionaries?branch=master
    :alt: coverage

.. image:: https://img.shields.io/pypi/v/dictionaries.svg?style=flat
    :target: https://pypi.python.org/pypi/dictionaries
    :alt: pypi

.. image:: https://img.shields.io/github/tag/pasztorpisti/py-dictionaries.svg?style=flat
    :target: https://github.com/pasztorpisti/py-dictionaries
    :alt: github

.. image:: https://img.shields.io/github/license/pasztorpisti/py-dictionaries.svg?style=flat
    :target: https://github.com/pasztorpisti/py-dictionaries/blob/master/LICENSE.txt
    :alt: license: MIT


.. contents::


Quick overview
==============

- Attribute-style item access is provided by all dictionary classes of this library.
- 5 dictionary implementations:

  - Standard dictionaries with attribute-style item access and a smarter ``copy()`` method with update parameters:

    - ``Dict``
    - ``OrderedDict``

  - Immutable/hashable versions of the previous two dictionaries:

    - ``FrozenDict``
    - ``FrozenOrderedDict``

  - A wrapper that can be used to create a readonly view of another dictionary instance:

    - ``ReadonlyDictProxy``


Installation
============

.. code-block:: sh

    pip install dictionaries

Alternatively you can download the distribution from the following places:

- https://pypi.python.org/pypi/dictionaries#downloads
- https://github.com/pasztorpisti/py-dictionaries/releases


Usage
=====


Quick-starter
-------------

After installing the library you can import the dictionary classes the following way:

.. code-block:: python

    from dictionaries import Dict, OrderedDict, FrozenDict, FrozenOrderedDict, ReadonlyDictProxy


Their interface is as standard as possible so I assume you know how to deal with them.


Attribute-style item access
---------------------------

The attribute-style dictionary item access can be really convenient in many cases but it has issues. The most
obvious issue is that the attributes of the dictionary are in conflict with your item keys.
For this reason attribute-style access is a little bit "stinky" (especially when you try to implement it) and
to aid this problem I've recently come up with a different kind of attribute-style access implementation. This
library provides both the usual way (discussed here and there) and also my method. (Yes, I know that providing 2 or
more ways isn't pythonic but you have to experiment to find out what works and what doesn't...) Later I might
drop one of them.


"Classic" attribute-style dict item access (as people know it)
..............................................................

As mentioned previously the attributes of the dictionary instance (like ``copy``) conflict with the keys of
your items. In order to be able to access dictionary methods we have to provide priority for the dictionary
attributes over the item keys.

.. code-block:: python

    >>> from dictionaries import Dict
    >>> d = Dict(copy=True, name='example')
    >>> d.my_item = 5   # this is equivalent to d['my_item'] = 5
    >>> d
    {'my_item': 5, 'name': 'example', 'copy': True}
    >>> d.my_item
    5
    >>> d.name
    'example'
    >>> d.copy          # the 'copy' item conflicts with the copy method!!!
    <bound method ExtendedCopyMixin.copy of {'my_item': 5, 'name': 'example', 'copy': True}>


Attribute-style item access through the ``items`` attribute of the dictionary
.............................................................................

My recent invention aids the previous conflict between dictionary attributes and item keys. By typing
a little bit more you can use attribute-style access without worrying about conflicts:

.. code-block:: python

    >>> from dictionaries import Dict
    >>> d = Dict(copy=True, name='example')
    >>> d.items.my_item = 5
    >>> d
    {'my_item': 5, 'name': 'example', 'copy': True}
    >>> d.items.my_item
    5
    >>> d.items.name
    'example'
    >>> d.items.copy
    True
    >>> d.items()       # using items() the good old way still works
    dict_items([('my_item', 5), ('name', 'example'), ('copy', True)])


You can use the ``items`` "method" of your dictionary the old way by calling it but you can also use it as an
object that provides attribute style access to your items. There are no conflicts because the only attributes
of ``items`` are the keys of your dictionary items.

Besides attribute-style item access the ``items`` attribute provides a limited set of the typical dictionary interface:

- ``__contains__``, ``__iter__``, ``__len__``
- Item assignment/retrieval/deletion with both attribute-style access and subscript notation.

This can be useful if you have to pass around the ``items`` object to be accessed elsewhere.

.. code-block:: python

    >>> from dictionaries import Dict
    >>> d = Dict(copy=True, name='example', my_item=5)
    >>> 'name' in d
    True
    >>> iter(d.items)
    <dict_keyiterator object at 0x104254e08>
    >>> list(d.items)
    ['my_item', 'name', 'copy']
    >>> len(d.items)
    3
    >>> del d.items['name']
    >>> del d.items.copy            # no conflict with Dict.copy :-)
    >>> d
    {'my_item': 5}


Dictionary classes
==================


``FrozenDict`` and ``FrozenOrderedDict``
----------------------------------------

These are "frozen"/immutable like the ``frozenset`` provided by the standard library. After creation
their value doesn't change during their lifetime. Like other immutable objects, instances of
these dictionaries are hashable given that all objects inside them are also hashable.

.. code-block:: python

    >>> from dictionaries import FrozenDict
    >>> d = FrozenDict(item1=1, item2=2)
    >>> d['item3'] = 3      # we shouldn't be able to modify an immutable object
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: 'FrozenDict' object does not support item assignment
    >>> del d['item2']      # we shouldn't be able to modify an immutable object
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: 'FrozenDict' object does not support item deletion
    >>> d
    <FrozenDict {'item1': 1, 'item2': 2}>
    >>> hash(d)
    8310388587437647073


``ReadonlyDictProxy``
---------------------

Sometimes you have to pass around some of your dictionaries but you want to make sure that no one modifies them. In this
case what you should do is creating a ``ReadonlyDictProxy`` wrapper around your dictionary and passing around the
wrapper instead of your original wrapped one. The ``ReadonlyDictProxy`` instance will delegate all requests to your
original dictionary except those requests that involve data modification (like item assignment/deletion, ``update()``,
etc...). Of course if you  modify the wrapped dictionary then the users of the readonly proxy will notice the changes.
The proxy keeps most of the behavior provided by the wrapped dict, for example if the wrapped dict is an ordered one
then the readonly proxy also behaves as ordered.

.. code-block:: python

    >>> from dictionaries import ReadonlyDictProxy, OrderedDict
    >>> wrapped = OrderedDict.fromkeys(['item1', 'item2', 'item3'])
    >>> proxy = ReadonlyDictProxy(wrapped)
    >>> wrapped
    OrderedDict([('item1', None), ('item2', None), ('item3', None)])
    >>> proxy
    <ReadonlyDictProxy OrderedDict([('item1', None), ('item2', None), ('item3', None)])>


Changes to the wrapped dict instance are reflected by the readonly proxy:

.. code-block:: python

    >>> del wrapped['item3']
    >>> wrapped['new_item'] = 'brand new'
    >>> wrapped
    OrderedDict([('item1', None), ('item2', None), ('new_item', 'brand new')])
    >>> proxy
    <ReadonlyDictProxy OrderedDict([('item1', None), ('item2', None), ('new_item', 'brand new')])>


Trying to modify the proxy object will fail:

.. code-block:: python

    >>> proxy['trying hard'] = 'to assign'      # the proxy is readonly, assignment fails
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: 'ReadonlyDictProxy' object does not support item assignment
    >>> del proxy['item1']                      # the proxy is readonly, deletion fails
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: 'ReadonlyDictProxy' object does not support item deletion


Copying a ``ReadonlyDictProxy`` instance with its ``copy`` method creates another
``ReadonlyDictProxy`` instance that wraps the exact same object:

.. code-block:: python

    >>> # Both of these statements create another wrapper/proxy around wrapped:
    >>> proxy_copy = proxy.copy()
    >>> proxy_copy2 = ReadonlyDictProxy(wrapped)
    >>>
    >>> # Now we have 3 proxy objects wrapping the same dictionary (wrapped):
    >>> wrapped.clear()
    >>> wrapped.items.woof = 'woof'
    >>> proxy
    <ReadonlyDictProxy OrderedDict([('woof', 'woof')])>
    >>> proxy_copy
    <ReadonlyDictProxy OrderedDict([('woof', 'woof')])>
    >>> proxy_copy2
    <ReadonlyDictProxy OrderedDict([('woof', 'woof')])>


Extended ``copy`` method
------------------------

All dictionary classes except ``ReadonlyDictProxy`` have a ``copy`` method that receives ``**kwargs``. These
keyword arguments are treated as dictionary items and used to create a copy that is updated with them.

.. code-block:: python

    >>> from dictionaries import Dict
    >>> d = Dict(a=0, b=1)
    >>> d2 = d.copy(b=2, c=3)
    >>> d
    {'a': 0, 'b': 1}
    >>> d2
    {'a': 0, 'b': 2, 'c': 3}
