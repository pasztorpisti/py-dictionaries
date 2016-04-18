from unittest import skip, skipIf, TestCase

import six

from dictionaries import Dict, OrderedDict, FrozenDict, FrozenOrderedDict, ReadonlyDictProxy

# Don't import classes from base directly to the namespace of this
# module in order to avoid discovering those base classes as tests.
from . import test_base


class TestDict(test_base.MutableDictTestBase):
    dict_class = Dict


class TestOrderedDict(test_base.MutableDictTestBase):
    dict_class = OrderedDict


class TestFrozenDict(test_base.ImmutableDictTestBase):
    dict_class = FrozenDict


class TestFrozenOrderedDict(test_base.ImmutableDictTestBase):
    dict_class = FrozenOrderedDict


class TestReadonlyDictProxy(test_base.ReadonlyDictTestBase):
    dict_class = ReadonlyDictProxy

    def _create_dict(self, *args, **kwargs):
        d = self.dict_class(dict(*args, **kwargs))
        self.assertIs(type(d), self.dict_class)
        return d

    @skip("ReadonlyDictProxy doesn't have an extended copy method that receives update parameters")
    def test_copy_with_update_parameters(self):
        pass

    @skip("ReadonlyDictProxy doesn't have a fromkeys method")
    def test_fromkeys(self):
        pass

    def test_the_copied_proxy_references_the_same_wrapped_data(self):
        wrapped_dict = dict(b=2)
        d = self.dict_class(wrapped_dict)
        d2 = d.copy()

        self.assertMappingEqual(wrapped_dict, dict(b=2))
        self.assertMappingEqual(d, dict(b=2))
        self.assertMappingEqual(d2, dict(b=2))

        wrapped_dict['c'] = 3

        self.assertMappingEqual(wrapped_dict, dict(b=2, c=3))
        self.assertMappingEqual(d, dict(b=2, c=3))
        self.assertMappingEqual(d2, dict(b=2, c=3))
