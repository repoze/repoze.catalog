import unittest

class TestCatalogIntFieldIndex(unittest.TestCase):

    def _class(self):
        from repoze.catalog.indexes.intfield import CatalogIntFieldIndex
        return CatalogIntFieldIndex

    def _make(self, *args, **kw):
        return self._class()(*args, **kw)

    def _make_default(self):
        def discriminator(value, default):
            return value

        return self._make(discriminator)

    def test_verifyImplements_ICatalogIndex(self):
        from zope.interface.verify import verifyClass
        from repoze.catalog.interfaces import ICatalogIndex
        verifyClass(ICatalogIndex, self._class())

    def test_verifyProvides_ICatalogIndex(self):
        from zope.interface.verify import verifyObject
        from repoze.catalog.interfaces import ICatalogIndex
        verifyObject(ICatalogIndex, self._make_default())

    def test_verifyImplements_IStatistics(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IStatistics
        verifyClass(IStatistics, self._class())

    def test_verifyProvides_IStatistics(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IStatistics
        verifyObject(IStatistics, self._make_default())

    def test_verifyImplements_IInjection(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IInjection
        verifyClass(IInjection, self._class())

    def test_verifyProvides_IInjection(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IInjection
        verifyObject(IInjection, self._make_default())

    def test_verifyImplements_IIndexSearch(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IIndexSearch
        verifyClass(IIndexSearch, self._class())

    def test_verifyProvides_IIndexSearch(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IIndexSearch
        verifyObject(IIndexSearch, self._make_default())

    def test_verifyImplements_IIndexSort(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IIndexSort
        verifyClass(IIndexSort, self._class())

    def test_verifyProvides_IIndexSort(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IIndexSort
        verifyObject(IIndexSort, self._make_default())

    def test_verifyImplements_IPersistent(self):
        from zope.interface.verify import verifyClass
        from persistent.interfaces import IPersistent
        verifyClass(IPersistent, self._class())

    def test_verifyProvides_IPersistent(self):
        from zope.interface.verify import verifyObject
        from persistent.interfaces import IPersistent
        verifyObject(IPersistent, self._make_default())

    def test_ctor(self):
        obj = self._make_default()
        self.assertEqual(len(obj._granular_indexes), 1)
        self.assertEqual(obj._granular_indexes[0][0], 1000)
        self.assertFalse(obj._granular_indexes[0][1])
        self.assertEqual(obj._num_docs(), 0)

    def test_index_doc_with_new_doc(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        self.assertEqual(sorted(obj._fwd_index.keys()), [9000])
        self.assertEqual(sorted(obj._fwd_index[9000]), [5])
        self.assertEqual(sorted(obj._rev_index.keys()), [5])
        self.assertEqual(obj._rev_index[5], 9000)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9])
        self.assertEqual(sorted(ndx[9]), [5])
        self.assertEqual(obj._num_docs(), 1)

    def test_index_doc_with_attr_discriminator(self):
        obj = self._make('x')
        obj.index_doc(5, DummyModel(x=9005))
        self.assertEqual(sorted(obj._fwd_index.keys()), [9005])
        self.assertEqual(sorted(obj._fwd_index[9005]), [5])
        self.assertEqual(sorted(obj._rev_index.keys()), [5])
        self.assertEqual(obj._rev_index[5], 9005)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9])
        self.assertEqual(sorted(ndx[9]), [5])
        self.assertEqual(obj._num_docs(), 1)

    def test_index_doc_with_discriminator_returns_default(self):
        def discriminator(obj, default):
            return default

        obj = self._make(discriminator)
        obj.index_doc(5, DummyModel())
        self.assertEqual(sorted(obj._fwd_index.keys()), [])
        self.assertEqual(sorted(obj._rev_index.keys()), [])
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [])
        self.assertEqual(obj._num_docs(), 0)

    def test_index_doc_with_non_integer_value(self):
        obj = self._make_default()
        self.assertRaises(ValueError, obj.index_doc, 5, 'x')

    def test_index_doc_with_changed_doc(self):
        obj = self._make_default()
        obj.index_doc(5, 14000)
        self.assertEqual(sorted(obj._fwd_index.keys()), [14000])
        self.assertEqual(sorted(obj._fwd_index[14000]), [5])
        self.assertEqual(sorted(obj._rev_index.keys()), [5])
        self.assertEqual(obj._rev_index[5], 14000)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [14])
        self.assertEqual(sorted(ndx[14]), [5])

        obj.index_doc(5, 9000)
        self.assertEqual(sorted(obj._fwd_index.keys()), [9000])
        self.assertEqual(sorted(obj._fwd_index[9000]), [5])
        self.assertEqual(sorted(obj._rev_index.keys()), [5])
        self.assertEqual(obj._rev_index[5], 9000)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9])
        self.assertEqual(sorted(ndx[9]), [5])
        self.assertEqual(obj._num_docs(), 1)

    def test_index_doc_with_no_changes(self):
        obj = self._make_default()
        for _i in range(2):
            obj.index_doc(5, 9000)
            self.assertEqual(sorted(obj._fwd_index.keys()), [9000])
            self.assertEqual(sorted(obj._fwd_index[9000]), [5])
            self.assertEqual(sorted(obj._rev_index.keys()), [5])
            self.assertEqual(obj._rev_index[5], 9000)
            ndx = obj._granular_indexes[0][1]
            self.assertEqual(sorted(ndx.keys()), [9])
            self.assertEqual(sorted(ndx[9]), [5])
        self.assertEqual(obj._num_docs(), 1)

    def test_index_doc_with_multiple_docs(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        self.assertEqual(sorted(obj._fwd_index.keys()), [9000, 9001, 11005])
        self.assertEqual(sorted(obj._fwd_index[9000]), [5, 6])
        self.assertEqual(sorted(obj._fwd_index[9001]), [7])
        self.assertEqual(sorted(obj._fwd_index[11005]), [8])
        self.assertEqual(sorted(obj._rev_index.keys()), [5, 6, 7, 8])
        self.assertEqual(obj._rev_index[5], 9000)
        self.assertEqual(obj._rev_index[6], 9000)
        self.assertEqual(obj._rev_index[7], 9001)
        self.assertEqual(obj._rev_index[8], 11005)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9, 11])
        self.assertEqual(sorted(ndx[9]), [5, 6, 7])
        self.assertEqual(sorted(ndx[11]), [8])
        self.assertEqual(obj._num_docs(), 4)

    def test_unindex_doc_with_normal_indexes(self):
        obj = self._make_default()
        obj.index_doc(5, 14000)
        obj.unindex_doc(5)
        self.assertEqual(sorted(obj._fwd_index.keys()), [])
        self.assertEqual(sorted(obj._rev_index.keys()), [])
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [])
        self.assertEqual(obj._num_docs(), 0)

    def test_unindex_doc_with_incomplete_trees(self):
        obj = self._make_default()
        obj.index_doc(5, 14000)
        del obj._fwd_index[14000]
        del obj._granular_indexes[0][1][14]
        obj.unindex_doc(5)
        self.assertEqual(sorted(obj._fwd_index.keys()), [])
        self.assertEqual(sorted(obj._rev_index.keys()), [])
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [])
        self.assertEqual(obj._num_docs(), 0)

    def test_apply_with_one_value(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        self.assertEqual(sorted(obj.apply(9001)), [7])

    def test_apply_with_two_values(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        q = {'query': [9001, 11005]}
        self.assertEqual(sorted(obj.apply(q)), [7, 8])

    def test_apply_with_small_range(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(9000, 9001)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7])

    def test_apply_with_large_range(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(8000, 10000)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7])

    def test_apply_with_multiple_ranges(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(8000, 10000), Range(11000, 11005)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7, 8])

    def test_apply_with_union_ranges(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(8000, 10000), Range(9001, 11005)],
            'operator': 'or'}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7, 8])

    def test_apply_with_intersecting_ranges(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(8000, 10000), Range(9001, 11005)],
            'operator': 'and'}
        self.assertEqual(sorted(obj.apply(q)), [7])

    def test_apply_with_range_that_excludes_9000(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(9001, 12000)]}
        self.assertEqual(sorted(obj.apply(q)), [7, 8])

    def test_apply_with_range_that_excludes_11006(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        obj.index_doc(9, 11006)
        from repoze.catalog import Range
        q = {'query': [Range(9000, 11005)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7, 8])

    def test_apply_without_maximum(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(9001, None)]}
        self.assertEqual(sorted(obj.apply(q)), [7, 8])

    def test_apply_without_minimum(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(None, 11004)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7])

    def test_apply_with_unbounded_range(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)

        # The operation should use _granular_indexes, not _fwd_index.
        del obj._fwd_index

        from repoze.catalog import Range
        q = {'query': [Range(None, None)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7, 8])

class Test_convert_field_to_intfield(unittest.TestCase):

    def _call(self, index, levels=(1000,)):
        from repoze.catalog.indexes.intfield import convert_field_to_intfield
        return convert_field_to_intfield(index, levels)

    def test_with_empty_index(self):
        def discriminator(value, default): return value
        from repoze.catalog.indexes.field import CatalogFieldIndex
        src = CatalogFieldIndex(discriminator)
        obj = self._call(src)
        self.assertEqual(sorted(obj._fwd_index.keys()), [])
        self.assertEqual(sorted(obj._rev_index.keys()), [])
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [])
        self.assertEqual(obj._num_docs(), 0)

    def test_with_contents(self):
        def discriminator(value, default):
            return value

        from repoze.catalog.indexes.field import CatalogFieldIndex
        src = CatalogFieldIndex(discriminator)
        src.index_doc(5, 9000)
        src.index_doc(6, 9000)
        src.index_doc(7, 9001)
        src.index_doc(8, 11005)

        obj = self._call(src)

        self.assertEqual(sorted(obj._fwd_index.keys()), [9000, 9001, 11005])
        self.assertEqual(sorted(obj._fwd_index[9000]), [5, 6])
        self.assertEqual(sorted(obj._fwd_index[9001]), [7])
        self.assertEqual(sorted(obj._fwd_index[11005]), [8])
        self.assertEqual(sorted(obj._rev_index.keys()), [5, 6, 7, 8])
        self.assertEqual(obj._rev_index[5], 9000)
        self.assertEqual(obj._rev_index[6], 9000)
        self.assertEqual(obj._rev_index[7], 9001)
        self.assertEqual(obj._rev_index[8], 11005)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9, 11])
        self.assertEqual(sorted(ndx[9]), [5, 6, 7])
        self.assertEqual(sorted(ndx[11]), [8])
        self.assertEqual(obj._num_docs(), 4)

class DummyModel(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)
        
