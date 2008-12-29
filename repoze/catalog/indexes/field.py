import bisect
import heapq
from itertools import islice

from zope.interface import implements

from zope.index.field import FieldIndex

from repoze.catalog.interfaces import ICatalogIndex
from repoze.catalog.indexes.common import CatalogIndex

_marker = []

class CatalogFieldIndex(CatalogIndex, FieldIndex):
    implements(ICatalogIndex)
    force_lazy = None # for unit testing
    force_nbest = None # for unit testing

    nbest_max_percent = .25 # "about a quarter of the size of the entire rs"

    def sort(self, docids, reverse=False, limit=None):
        if limit is not None:
            limit = int(limit)
            if limit < 1:
                raise ValueError('limit must be 1 or greater')

        if not docids:
            raise StopIteration
            
        numdocs = self._num_docs.value
        if not numdocs:
            raise StopIteration

        rev_index = self._rev_index
        fwd_index = self._fwd_index

        rlen = len(docids)

        # use_lazy computation lifted wholesale from Zope2 catalog
        # without questioning algorithm.  We use "lazy" sorting when
        # the size of the result set is much larger than the number of
        # documents in this index.
        use_lazy = (rlen > (numdocs * (rlen / 100 + 1)))

        # use n-best when the limit argument limits to fewer than
        # self.nbest_max_percent % of the total number of results (see
        # http://www.zope.org/Members/Caseman/ZCatalog_for_2.6.1 for
        # overall explanation of n-best)
        use_nbest = ( (limit and (limit/float(rlen) < self.nbest_max_percent)) )

        if self.force_nbest is not None:
            use_nbest = self.force_nbest
        if self.force_lazy is not None:
            use_lazy = self.force_lazy

        marker = _marker

        if use_nbest:
            # this is a sort with a limit that appears useful, and the
            # limit argument limits to fewer than
            # self.nbest_max_percent % of the total number of results,
            # try to take advantage of the fact that we can keep a
            # smaller set of simultaneous values in memory; use
            # generators and heapq functions to do so.
            if reverse:
                # we use a generator as an iterable in the reverse
                # sort case because the nlargest implementation does
                # not manifest the whole thing into memory at once if
                # we do so.
                iterable = nsort(docids, rev_index)
                for val in heapq.nlargest(limit, iterable):
                    yield val[1]

            else:
                # lifted from heapq.nsmallest
                if limit * 10 <=  rlen:
                    iterable = nsort(docids, rev_index)
                    it = iter(iterable)
                    result = sorted(islice(it, 0, limit))
                    if not result:
                        yield StopIteration
                    insort = bisect.insort
                    pop = result.pop
                    los = result[-1]    # los --> Largest of the nsmallest
                    for elem in it:
                        if los <= elem:
                            continue
                        insort(result, elem)
                        pop()
                        los = result[-1]
                else:
                    h = []
                    for docid in docids:
                        val = rev_index.get(docid, marker)
                        if val is not marker:
                            h.append((val, docid))
                    heapq.heapify(h)
                    result = map(heapq.heappop,
                                 heapq.repeat(h, min(limit, len(h))))

                for val in result:
                    yield val[1]

        elif use_lazy:
            # If the number of results in the search result set is
            # much larger than the number of items in this index, we
            # assume it will be fastest to iterate over the keys or
            # values one of our indexes.

            if reverse:
                # Our reverse index is a mapping from a docid to its
                # value.  Calling byValue on our reverse index returns
                # a *fully materialized* list (not a generator) of
                # (value, docid) tuples in reverse-value order.  The
                # None passed to byValue is a *minimum value* (this
                # seems like a broken API).
                n = 0
                for value, docid in rev_index.byValue(None):
                    if docid in docids:
                        if limit and n >= limit:
                            raise StopIteration
                        n += 1
                        yield docid

            else:
                # Our forward index is a mapping from value to set of
                # docids.  If we're sorting in ascending order, pick
                # off docids from our forward BTree's values, as its
                # keys are already sorted in ascending sort-value
                # order.
                n = 0
                for stored_docids in fwd_index.values():
                    isect = self.family.IF.intersection(docids, stored_docids)
                    for docid in isect:
                        if limit and n >= limit:
                            raise StopIteration
                        n += 1
                        yield docid
        else:
            # If the result set isn't much larger than the number of
            # documents in this index and we can't use n-best, use a
            # non-lazy sort.
            n = 0
            for docid in sorted(docids, key=rev_index.get, reverse=reverse):
                if rev_index.get(docid, marker) is not marker:
                    # we skip docids that are not in this index (as
                    # per Z2 catalog implementation)
                    if limit and n >= limit:
                        raise StopIteration
                    n += 1
                    yield docid

    def unindex_doc(self, docid):
        """See interface IInjection.

        Base class overridden to be able to unindex None values. """
        rev_index = self._rev_index
        value = rev_index.get(docid, _marker)
        if value is _marker:
            return # not in index

        del rev_index[docid]

        try:
            set = self._fwd_index[value]
            set.remove(docid)
        except KeyError:
            # This is fishy, but we don't want to raise an error.
            # We should probably log something.
            # but keep it from throwing a dirty exception
            set = 1

        if not set:
            del self._fwd_index[value]

        self._num_docs.change(-1)
                
def nsort(docids, rev_index, marker=_marker):
    for docid in docids:
        val = rev_index.get(docid, marker)
        if val is not marker:
            yield (val, docid)
