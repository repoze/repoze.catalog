from zope.interface import implements

from zope.index.interfaces import IStatistics
from repoze.catalog.interfaces import ICatalogIndex

from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog import Range

from BTrees.Length import Length

_marker = object()

class CatalogIntFieldIndex(CatalogFieldIndex):
    """Indexes integer values using multiple granularity levels.

    The multiple levels of granularity make it possible to query large ranges
    without loading as many IFTreeSets from the forward index as when a
    regular CatalogFieldIndex is used.
    """
    implements(ICatalogIndex, IStatistics)

    def __init__(self, discriminator, levels=(1000,)):
        """Create an index.
        
        ``levels`` is a sequence of integer coarseness levels.  The default
        is (1000,).
        """
        self._levels = tuple(levels)
        super(CatalogIntFieldIndex, self).__init__(discriminator)

    def clear(self):
        """Initialize all mappings."""
        # The forward index maps an indexed value to IFSet(docids)
        self._fwd_index = self.family.IO.BTree()
        # The reverse index maps a docid to its index value
        self._rev_index = self.family.II.BTree()
        self._num_docs = Length(0)
        # self._granular_indexes: [(level, BTree(value -> IFSet([docid])))]
        self._granular_indexes = [(level, self.family.IO.BTree())
            for level in self._levels]

    def index_doc(self, docid, obj):
        if callable(self.discriminator):
            value = self.discriminator(obj, _marker)
        else:
            value = getattr(obj, self.discriminator, _marker)

        if value is _marker:
            # unindex the previous value
            self.unindex_doc(docid)
            return

        if not isinstance(value, int):
            raise ValueError(
                'GranularIndex cannot index non-integer value %s' % value)

        rev_index = self._rev_index
        if docid in rev_index:
            if docid in self._fwd_index.get(value, ()):
                # There's no need to index the doc; it's already up to date.
                return
            # unindex doc if present
            self.unindex_doc(docid)

        # Insert into forward index.
        set = self._fwd_index.get(value)
        if set is None:
            set = self.family.IF.TreeSet()
            self._fwd_index[value] = set
        set.insert(docid)

        # increment doc count
        self._num_docs.change(1)

        # Insert into reverse index.
        rev_index[docid] = value

        for level, ndx in self._granular_indexes:
            v = value // level
            set = ndx.get(v)
            if set is None:
                set = self.family.IF.TreeSet()
                ndx[v] = set
            set.insert(docid)

    def unindex_doc(self, docid):
        rev_index = self._rev_index
        value = rev_index.get(docid)
        if value is None:
            return  # not in index

        del rev_index[docid]

        self._num_docs.change(-1)

        ndx = self._fwd_index
        try:
            set = ndx[value]
            set.remove(docid)
            if not set:
                del ndx[value]
        except KeyError:
            pass

        for level, ndx in self._granular_indexes:
            v = value // level
            try:
                set = ndx[v]
                set.remove(docid)
                if not set:
                    del ndx[v]
            except KeyError:
                pass

    def search(self, queries, operator='or'):
        sets = []
        for query in queries:
            if isinstance(query, Range):
                query = query.as_tuple()
            else:
                query = (query, query)

            set = self.family.IF.multiunion(self.docids_in_range(*query))
            sets.append(set)

        result = None

        if len(sets) == 1:
            result = sets[0]
        elif operator == 'and':
            sets.sort()
            for set in sets:
                result = self.family.IF.intersection(set, result)
        else:
            result = self.family.IF.multiunion(sets)

        return result

    def docids_in_range(self, min, max):
        """List the docids for an integer range, inclusive on both ends.

        min or max can be None, making them unbounded.

        Returns an iterable of IFSets.
        """
        for level, ndx in sorted(self._granular_indexes, reverse=True):
            # Try to fill the range using coarse buckets first.
            # Use only buckets that completely fill the range.
            # For example, if start is 2 and level is 10, then we can't
            # use bucket 0; only buckets 1 and greater are useful.
            # Similarly, if end is 18 and level is 10, then we can't use
            # bucket 1; only buckets 0 and less are useful.
            if min is not None:
                a = (min + level - 1) // level
            else:
                a = None
            if max is not None:
                b = (max - level + 1) // level
            else:
                b = None
            # a and b are now coarse bucket values (or None).
            if a is None or b is None or a <= b:
                sets = []
                if a is not None and min < a * level:
                    # include the gap before
                    sets.extend(self.docids_in_range(min, a * level - 1))
                sets.extend(ndx.values(a, b))
                if b is not None and (b + 1) * level - 1 < max:
                    # include the gap after
                    sets.extend(self.docids_in_range((b + 1) * level, max))
                return sets

        return self._fwd_index.values(min, max)


def convert_field_to_intfield(index, levels=(1000,)):
    """Create a IntFieldIndex from a FieldIndex.  Returns the new index.

    Copies the data without resolving the objects.
    """
    g = CatalogIntFieldIndex(index.discriminator, levels=levels)
    treeset = g.family.IF.TreeSet
    for value, docids in index._fwd_index.iteritems():
        g._fwd_index[value] = treeset(docids)
        for level, ndx in g._granular_indexes:
            v = value // level
            set = ndx.get(v)
            if set is None:
                set = treeset()
                ndx[v] = set
            set.update(docids)
    g._rev_index.update(index._rev_index)
    g._num_docs.value = index._num_docs()
    return g
