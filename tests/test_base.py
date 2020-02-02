import itertools
import numbers
import random
import sys
from unittest import TestCase, TestSuite

try:
    # python 3.3+
    from collections.abc import Hashable
except ImportError:
    from collections import Hashable

import six


class ExtendedTestCase(TestCase):
    def assertMappingEqual(self, m1, m2, msg=None):
        # Since our test keys and values are hashable we can use unittest
        # set comparison because it has easy to read diff output.
        self.assertSetEqual(set(m1.items()), set(m2.items()), msg)

    if sys.version_info < (3, 2):
        assertRaisesRegex = TestCase.assertRaisesRegexp


class DictTestCase(ExtendedTestCase):
    dict_class = None

    def _create_dict(self, *args, **kwargs):
        d = self.dict_class(*args, **kwargs)
        self.assertIs(type(d), self.dict_class)
        return d


class MutableDictStressTests(DictTestCase):
    def test_add_remove_add_remove_a_lot_of_items(self):
        item_count = 10000
        items = [('key_%s' % n, 'value_%s' % n) for n in range(item_count)]
        random.shuffle(items)
        first_half = items[:item_count//2]
        second_half = items[item_count//2:]

        d = self._create_dict(first_half)
        self.assertMappingEqual(d, dict(first_half))

        for key, value in second_half:
            d[key] = value
        self.assertMappingEqual(d, dict(items))

        for key, _ in first_half:
            del d[key]
        self.assertMappingEqual(d, dict(second_half))

        for key, _ in second_half:
            del d[key]
        self.assertMappingEqual(d, {})


class DictInitTests(DictTestCase):
    def test_init_with_no_args(self):
        d = self._create_dict()
        self.assertMappingEqual(d, {})

    def test_init_with_kwargs(self):
        d = self._create_dict(b=2, c=3)
        self.assertMappingEqual(d, dict(b=2, c=3))

    def test_init_with_mapping(self):
        d = self._create_dict(dict(b=2, c=3))
        self.assertMappingEqual(d, dict(b=2, c=3))

    def test_init_with_mapping_and_kwargs(self):
        d = self._create_dict(dict(b=2, c=3), c=4, d=5)
        self.assertMappingEqual(d, dict(b=2, c=4, d=5))

    def test_init_with_iterable(self):
        d = self._create_dict([('b', 2), ('c', 3)])
        self.assertMappingEqual(d, dict(b=2, c=3))

    def test_init_with_iterable_and_kwargs(self):
        d = self._create_dict([('b', 2), ('c', 3)], c=4, d=5)
        self.assertMappingEqual(d, dict(b=2, c=4, d=5))


class CommonDictTests(DictInitTests, DictTestCase):
    """ Tests that are common for mutable and readonly dictionaries. """
    def test_iter(self):
        d = self._create_dict()
        self.assertSetEqual(set(iter(d.items)), set())
        self.assertSetEqual(set(iter(d.items)), set())
        self.assertSetEqual(set(iter(d)), set())
        self.assertSetEqual(set(iter(d)), set())

        d = self._create_dict(b=2, c=3)
        self.assertSetEqual(set(iter(d.items)), {'b', 'c'})
        self.assertSetEqual(set(iter(d.items)), {'b', 'c'})
        self.assertSetEqual(set(iter(d)), {'b', 'c'})
        self.assertSetEqual(set(iter(d)), {'b', 'c'})

    def test_len(self):
        d = self._create_dict()
        self.assertEqual(len(d.items), 0)
        self.assertEqual(len(d), 0)
        d = self._create_dict(b=2)
        self.assertEqual(len(d.items), 1)
        self.assertEqual(len(d), 1)
        d = self._create_dict(b=2, c=3)
        self.assertEqual(len(d.items), 2)
        self.assertEqual(len(d), 2)

    def test_contains(self):
        d = self._create_dict(b=2, c=3)
        self.assertFalse('a' in d.items)
        self.assertTrue('b' in d.items)
        self.assertFalse('a' in d)
        self.assertTrue('b' in d)

    def test_getattribute(self):
        """ Our dictionaries allow access to items through getattribute. """
        d = self._create_dict(b=2, c=3)

        self.assertFalse(hasattr(d, 'a'))
        self.assertTrue(hasattr(d, 'b'))
        self.assertFalse(hasattr(d.items, 'a'))
        self.assertTrue(hasattr(d.items, 'b'))

        self.assertRaises(AttributeError, getattr, d, 'a')
        self.assertEqual(d.b, 2)
        self.assertEqual(d.c, 3)
        self.assertRaises(AttributeError, getattr, d.items, 'a')
        self.assertEqual(d.items.b, 2)
        self.assertEqual(d.items.c, 3)

    def test_getitem(self):
        d = self._create_dict(b=2, c=3)
        self.assertEqual(d.items['b'], 2)
        self.assertEqual(d['b'], 2)

        with self.assertRaises(KeyError):
            item = d.items['a']

        with self.assertRaises(KeyError):
            item = d['a']

    def test_copy(self):
        d = self._create_dict(b=2, c=3)
        d2 = d.copy()
        self.assertIs(type(d), self.dict_class)
        self.assertIs(type(d2), self.dict_class)
        self.assertMappingEqual(d, dict(b=2, c=3))
        self.assertMappingEqual(d2, dict(b=2, c=3))

    def test_copy_with_update_parameters(self):
        d = self._create_dict(b=2, c=3)
        d2 = d.copy(c=4, d=5)
        self.assertIs(type(d), self.dict_class)
        self.assertIs(type(d2), self.dict_class)
        self.assertMappingEqual(d, dict(b=2, c=3))
        self.assertMappingEqual(d2, dict(b=2, c=4, d=5))

    def test_fromkeys(self):
        keys = ['key0', 'key1']

        d = self.dict_class.fromkeys(keys)
        self.assertIs(type(d), self.dict_class)
        self.assertMappingEqual(d, dict(key0=None, key1=None))

        d = self.dict_class.fromkeys(keys, 'value')
        self.assertIs(type(d), self.dict_class)
        self.assertMappingEqual(d, dict(key0='value', key1='value'))

    def test_get(self):
        d = self._create_dict(b=2, c=3)
        self.assertIsNone(d.get('a'))
        self.assertEqual(d.get('a', 'default'), 'default')
        self.assertEqual(d.get('b'), 2)
        self.assertEqual(d.get('b', 'default'), 2)

    def test_items(self):
        d = self._create_dict(b=2, c=3)
        items = set(d.items())
        self.assertSetEqual(items, {('b', 2), ('c', 3)})

    def test_keys(self):
        d = self._create_dict(b=2, c=3)
        keys = set(d.keys())
        self.assertSetEqual(keys, {'b', 'c'})

    def test_values(self):
        d = self._create_dict(b=2, c=3)
        values = set(d.values())
        self.assertSetEqual(values, {2, 3})

    if six.PY2:
        def test_iteritems(self):
            d = self._create_dict(b=2, c=3)
            items = set(d.iteritems())
            self.assertSetEqual(items, {('b', 2), ('c', 3)})

        def test_iterkeys(self):
            d = self._create_dict(b=2, c=3)
            keys = set(d.iterkeys())
            self.assertSetEqual(keys, {'b', 'c'})

        def test_itervalues(self):
            d = self._create_dict(b=2, c=3)
            values = set(d.itervalues())
            self.assertSetEqual(values, {2, 3})

    def test_eq(self):
        d = self._create_dict(b=2, c=3)
        self.assertTrue(d == dict(b=2, c=3))
        self.assertFalse(d == dict(b=1, c=3))
        self.assertFalse(d == dict(a=2, c=3))
        self.assertFalse(d == dict(c=3))

    def test_ne(self):
        d = self._create_dict(b=2, c=3)
        self.assertFalse(d != dict(b=2, c=3))
        self.assertTrue(d != dict(b=1, c=3))
        self.assertTrue(d != dict(a=2, c=3))
        self.assertTrue(d != dict(c=3))

    def test_hash(self):
        self.assertNotIsInstance(self._create_dict(), Hashable)

    def test_str(self):
        s = str(self._create_dict(b=2, c=3))
        self.assertIsInstance(s, six.string_types)

    def test_repr(self):
        s = repr(self._create_dict(b=2, c=3))
        self.assertIsInstance(s, six.string_types)


class MutableDictTestBase(MutableDictStressTests, CommonDictTests):
    def test_clear(self):
        d = self._create_dict(b=2, c=3)
        self.assertMappingEqual(d, dict(b=2, c=3))
        d.clear()
        self.assertMappingEqual(d, {})

    def test_setattr(self):
        d = self._create_dict(b=2, c=3)
        d.items.d = 4
        self.assertMappingEqual(d, dict(b=2, c=3, d=4))
        d.items.c = 5
        self.assertMappingEqual(d, dict(b=2, c=5, d=4))

        d = self._create_dict(b=2, c=3)
        d.d = 4
        self.assertMappingEqual(d, dict(b=2, c=3, d=4))
        d.c = 5
        self.assertMappingEqual(d, dict(b=2, c=5, d=4))

    def test_delattr(self):
        d = self._create_dict(b=2, c=3)

        with self.assertRaises(AttributeError):
            del d.items.d

        self.assertMappingEqual(d, dict(b=2, c=3))
        del d.items.c
        self.assertMappingEqual(d, dict(b=2))

        d = self._create_dict(b=2, c=3)

        with self.assertRaises(AttributeError):
            del d.d
        self.assertMappingEqual(d, dict(b=2, c=3))
        del d.c
        self.assertMappingEqual(d, dict(b=2))

    def test_setitem(self):
        d = self._create_dict(b=2, c=3)
        d.items['d'] = 4
        self.assertMappingEqual(d, dict(b=2, c=3, d=4))
        d.items['c'] = 5
        self.assertMappingEqual(d, dict(b=2, c=5, d=4))

        d = self._create_dict(b=2, c=3)
        d['d'] = 4
        self.assertMappingEqual(d, dict(b=2, c=3, d=4))
        d['c'] = 5
        self.assertMappingEqual(d, dict(b=2, c=5, d=4))

    def test_delitem(self):
        d = self._create_dict(b=2, c=3)

        with self.assertRaises(KeyError):
            del d.items['d']
        self.assertMappingEqual(d, dict(b=2, c=3))
        del d.items['c']
        self.assertMappingEqual(d, dict(b=2))

        d = self._create_dict(b=2, c=3)

        with self.assertRaises(KeyError):
            del d['d']
        self.assertMappingEqual(d, dict(b=2, c=3))
        del d['c']
        self.assertMappingEqual(d, dict(b=2))

    def test_pop(self):
        d = self._create_dict(b=2, c=3)
        self.assertRaises(KeyError, d.pop, 'd')
        self.assertEqual(d.pop('d', 4), 4)
        self.assertMappingEqual(d, dict(b=2, c=3))
        self.assertEqual(d.pop('c'), 3)
        self.assertMappingEqual(d, dict(b=2))
        self.assertRaises(KeyError, d.pop, 'c')
        self.assertEqual(d.pop('b', 42), 2)
        self.assertMappingEqual(d, {})
        self.assertEqual(d.pop('b', 4), 4)
        self.assertIsNone(d.pop('b', None))

    def test_popitem(self):
        d = self._create_dict(b=2, c=3)
        item = d.popitem()
        self.assertEqual(len(d), 1)
        item2 = d.popitem()
        self.assertMappingEqual(d, {})
        self.assertRaises(KeyError, d.popitem)
        self.assertSetEqual({item, item2}, {('b', 2), ('c', 3)})

    def test_setdefault(self):
        d = self._create_dict(b=2)
        res = d.setdefault('c', 3)
        self.assertEqual(res, 3)
        self.assertMappingEqual(d, dict(b=2, c=3))
        res = d.setdefault('b', 3)
        self.assertEqual(res, 2)
        self.assertMappingEqual(d, dict(b=2, c=3))

    def test_update(self):
        d = self._create_dict(b=2, c=3)
        d.update(dict(c=4, d=5))
        self.assertMappingEqual(d, dict(b=2, c=4, d=5))


class ReadonlyDictTestBase(CommonDictTests):
    def test_clear(self):
        self.assertFalse(hasattr(self.dict_class, 'clear'))
        self.assertFalse(hasattr(self._create_dict(), 'clear'))

    def test_pop(self):
        self.assertFalse(hasattr(self.dict_class, 'pop'))
        self.assertFalse(hasattr(self._create_dict(), 'pop'))

    def test_popitem(self):
        self.assertFalse(hasattr(self.dict_class, 'popitem'))
        self.assertFalse(hasattr(self._create_dict(), 'popitem'))

    def test_setdefault(self):
        self.assertFalse(hasattr(self.dict_class, 'setdefault'))
        self.assertFalse(hasattr(self._create_dict(), 'setdefault'))

    def test_update(self):
        self.assertFalse(hasattr(self.dict_class, 'update'))
        self.assertFalse(hasattr(self._create_dict(), 'update'))

    def test_setattr(self):
        d = self._create_dict(b=2, c=3)
        with self.assertRaisesRegex(AttributeError, r"Item assignment through attribute access isn't supported"):
            d.items.d = 4
        self.assertMappingEqual(d, dict(b=2, c=3))

        try:
            setattr(d, 'd', 5)
        except (TypeError, AttributeError):
            pass
            # When __slots__ do their job an exception is raised, otherwise setattr will set an
            # instance attribute on the dict instance instead of assigning a dict item.
        finally:
            self.assertMappingEqual(d, dict(b=2, c=3))

    def test_delattr(self):
        d = self._create_dict(b=2, c=3)

        with self.assertRaises(AttributeError):
            del d.items.c
        self.assertMappingEqual(d, dict(b=2, c=3))

        with self.assertRaises(AttributeError):
            del d.c
        self.assertMappingEqual(d, dict(b=2, c=3))

    def test_setitem(self):
        d = self._create_dict(b=2, c=3)

        with self.assertRaises(TypeError):
            d.items['d'] = 4
        self.assertMappingEqual(d, dict(b=2, c=3))

        with self.assertRaises(TypeError):
            d['d'] = 4
        self.assertMappingEqual(d, dict(b=2, c=3))

    def test_delitem(self):
        d = self._create_dict(b=2, c=3)

        with self.assertRaises(TypeError):
            del d.items['c']
        self.assertMappingEqual(d, dict(b=2, c=3))

        with self.assertRaises(TypeError):
            del d['c']
        self.assertMappingEqual(d, dict(b=2, c=3))


class ImmutableDictTestBase(ReadonlyDictTestBase):
    """ With my current interpretation the difference between a readonly and an immutable dictionary is that
    the data of an immutable dictionary never changes during its lifetime while a readonly dictionary might
    change as a result of external factors. For example in case of a readonly dict proxy you can not change the
    readonly dict proxy object reference to change the data of the dict but the proxied dictionary can be
    changed elsewhere if someone has a reference to it. In case of an immutable dict the data is guaranteed
    to be 'frozen'. """
    def test_hash(self):
        d = self._create_dict(b=2, c=3)
        hash_value = hash(d)
        self.assertIsInstance(hash_value, numbers.Integral)

        # A stupid test:
        # Building up the same dictionary by inserting the same items
        # in a different order should result in the same hash value.
        items = [('item_%s' % n, n) for n in range(5)]
        hash_values = [hash(self._create_dict(permutation)) for permutation in itertools.permutations(items)]
        self.assertEqual(len(set(hash_values)), 1)

    def test_copy_with_no_args_returns_self(self):
        d = self._create_dict(b=2, c=3)
        d2 = d.copy()
        self.assertIs(d, d2)


# Excluding all tests from this module since their sole
# purpose is to be used as base classes in other modules.
def load_tests(loader, tests, pattern):
    return TestSuite()
