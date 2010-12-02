
from BTrees.Interfaces import IBTreeModule
from BTrees.Interfaces import IIMerge
from repoze.catalog.interfaces import IMergeAdapter
from zope.interface import implements
import BTrees


class AdaptableBTreeModule(object):
    """IBTreeModule-like object that can merge different kinds of collections.

    When merging collections, this object asks each collection
    (if the collection provides IMergeAdapter) for
    a collection operations module compatible with both collections.
    If a compatible module is found, this object calls it to do the work.
    """
    implements(IBTreeModule, IIMerge)

    def __init__(self, default_module):
        self.default_module = default_module
        self.BTree = default_module.BTree
        self.Bucket = default_module.Bucket
        self.TreeSet = default_module.TreeSet
        self.Set = default_module.Set
        self.compatible_types = (
            self.Set,
            self.TreeSet,
            self.BTree,
            self.Bucket,
        )

    def _get_module(self, c1, c2):
        if isinstance(c1, self.compatible_types):
            if isinstance(c2, self.compatible_types):
                return self.default_module
        for obj in c1, c2:
            # Try to get a module compatible with both sets.
            if IMergeAdapter.providedBy(obj):
                module = obj.get_module(c1, c2)
                if module is not NotImplemented:
                    return module
        raise TypeError("No set adapter provided for (%r, %r)." % (c1, c2))

    def difference(self, c1, c2):
        """Return the keys or items in c1 for which there is no key in c2.

        If c1 is None, then None is returned.  If c2 is None, then c1
        is returned.

        If neither c1 nor c2 is None, the output is a Set if c1 is a Set or
        TreeSet, and is a Bucket if c1 is a Bucket or BTree.
        """
        if c1 is None or c2 is None:
            return c1
        return self._get_module(c1, c2).difference(c1, c2)

    def union(self, c1, c2):
        """Compute the Union of c1 and c2.

        If c1 is None, then c2 is returned, otherwise, if c2 is None,
        then c1 is returned.

        The output is a Set containing keys from the input
        collections.
        """
        if c1 is None:
            return c2
        if c2 is None:
            return c1
        return self._get_module(c1, c2).union(c1, c2)

    def intersection(self, c1, c2):
        """Compute the intersection of c1 and c2.

        If c1 is None, then c2 is returned, otherwise, if c2 is None,
        then c1 is returned.

        The output is a Set containing matching keys from the input
        collections.
        """
        if c1 is None:
            return c2
        if c2 is None:
            return c1
        return self._get_module(c1, c2).intersection(c1, c2)

    def weightedUnion(self, c1, c2, weight1=1, weight2=1):
        """Compute the weighted union of c1 and c2.

        If c1 and c2 are None, the output is (0, None).

        If c1 is None and c2 is not None, the output is (weight2, c2).

        If c1 is not None and c2 is None, the output is (weight1, c1).

        Else, and hereafter, c1 is not None and c2 is not None.

        If c1 and c2 are both sets, the output is 1 and the (unweighted)
        union of the sets.

        Else the output is 1 and a Bucket whose keys are the union of c1 and
        c2's keys, and whose values are::

          v1*weight1 + v2*weight2

          where:

            v1 is 0        if the key is not in c1
                  1        if the key is in c1 and c1 is a set
                  c1[key]  if the key is in c1 and c1 is a mapping

            v2 is 0        if the key is not in c2
                  1        if the key is in c2 and c2 is a set
                  c2[key]  if the key is in c2 and c2 is a mapping

        Note that c1 and c2 must be collections.
        """
        if c1 is None:
            if c2 is None:
                return (0, None)
            else:
                return (weight2, c2)
        if c2 is None:
            return (weight1, c1)
        return self._get_module(c1, c2).weightedUnion(c1, c2)

    def weightedIntersection(self, c1, c2, weight1=1, weight2=1):
        """Compute the weighted intersection of c1 and c2.

        If c1 and c2 are None, the output is (0, None).

        If c1 is None and c2 is not None, the output is (weight2, c2).

        If c1 is not None and c2 is None, the output is (weight1, c1).

        Else, and hereafter, c1 is not None and c2 is not None.

        If c1 and c2 are both sets, the output is the sum of the weights
        and the (unweighted) intersection of the sets.

        Else the output is 1 and a Bucket whose keys are the intersection of
        c1 and c2's keys, and whose values are::

          v1*weight1 + v2*weight2

          where:

            v1 is 1        if c1 is a set
                  c1[key]  if c1 is a mapping

            v2 is 1        if c2 is a set
                  c2[key]  if c2 is a mapping

        Note that c1 and c2 must be collections.
        """
        if c1 is None:
            if c2 is None:
                return (0, None)
            else:
                return (weight2, c2)
        if c2 is None:
            return (weight1, c1)
        return self._get_module(c1, c2).weightedIntersection(c1, c2)


class AdaptableBTreeFamily(object):

    def __init__(self, family):
        self.IF = AdaptableBTreeModule(family.IF)


adaptable_family32 = AdaptableBTreeFamily(BTrees.family32)
