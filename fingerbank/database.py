"""A database of DHCP fingerprints"""
from fingerbank.objects import Group, System
from bisect import bisect_left

class RangeP(object):
    """
    range pair. the purpose of this class is to provide a nice way to binary
    search a list of somethings to find the range that contains an int. this
    is the something.

    We do all these contortions so we can 

    See GroupLookup for a usage example.
    """
    def __init__(self, lo, hi):
        """
        Create a new range with a lower and upper bound, inclusive

        >>> p = RangeP(5, 10)
        >>> p.hi == 10
        True
        >>> p.lo == 5
        True
        >>> p2 = RangeP(10, 5)
        Traceback (most recent call last):
            ...
        ValueError: range cannot have lo 10 > hi 5
        """
        if lo > hi:
            raise ValueError("range cannot have lo {l} > hi {h}".format(
                l=lo, h=hi))
        self.lo = lo
        self.hi = hi

    def __str__(self):
        """
        >>> str(RangeP(5, 10))
        '(5..10)'
        """
        return "({0}..{1})".format(self.lo, self.hi)

    def __repr__(self):
        """
        >>> repr(RangeP(5, 10))
        'RangeP(5, 10)'
        """
        return "RangeP({lo}, {hi})".format(
                lo=repr(self.lo), hi=repr(self.hi))

    def __cmp__(self, other):
        """
        Kinda a hack. When a RangeP is compared to an it, it is considered equal
        if the int is in the range.

        Otherwise, ranges compared by adjoining endpoints, and if they intersect,
        we freak the fuck out.

        >>> hi = RangeP(50, 100)
        >>> lo = RangeP(1, 49)

        range v range checks
        >>> hi > lo
        True
        >>> lo < hi
        True
        >>> hi == lo
        False

        range v number checks
        >>> hi == 5
        False
        >>> hi == 55
        True
        >>> hi > 200
        False
        >>> hi > 5
        True
        >>> hi < 200
        True
        >>> hi < 5
        False

        intersecting ranges are evil
        >>> lo = RangeP(1, 55)
        >>> hi > lo
        Traceback (most recent call last):
            ...
        ValueError: ranges intersect! (50..100), (1..55)
        >>> lo < hi
        Traceback (most recent call last):
            ...
        ValueError: ranges intersect! (1..55), (50..100)
        """
        if isinstance(other, int):
            if self.hi < other:
                return -1
            if self.lo > other:
                return 1
            return 0 # consider equal to an int if we contain it

        # handle non-intersecting ranges
        if self.hi < other.lo:
            return -1

        if self.lo > other.hi:
            return 1

        if self.lo == other.lo and self.hi == other.hi:
            return 0

        # otherwise freak out
        raise ValueError("ranges intersect! {0}, {1}".format(self, other))

    def includes(self, n):
        """true iff n is in this range"""
        return self.lo <= n <= self.hi


class GroupLookup(object):
    """
    better-than-linear-search group lookup.
    """
    def __init__(self, groups):
        if groups is None:
            return

        ranges = []
        self.range_to_group = {}
        for group in groups:
            for lo, hi in group.ranges:
                rp = RangeP(lo, hi)
                self.range_to_group[rp] = group
                ranges.append(rp)

        # ranges pre-sorted
        self.ranges = sorted(ranges)

    @staticmethod
    def binary_search(a, x, lo=0, hi=None):
        """
        find the position of element x in array a, between lo and hi.
        returns -1 if x was not found, and the index of x otherwise.
        uses built-in comparators.
        >>> gl = GroupLookup(None)
        >>> a = [0,1,2,3,4,5]
        >>> x = 3
        >>> gl.binary_search(a, x)
        3
        >>> gl.binary_search(a, 500)
        -1
        """
        hi = hi or len(a)
        # bisect_left is fast bisection insert search
        # see http://hg.python.org/cpython/file/2.7/Lib/bisect.py
        pos = bisect_left(a, x, lo, hi)
        if pos != hi and a[pos] == x:
            return pos
        else:
            return -1 # not found
        
    def get_group(self, system):
        pos = self.binary_search(self.ranges, system.number)
        if pos == -1:
            return None
        rp = self.ranges[pos]
        return self.range_to_group[rp]


class SystemLookup(object):
    """
    fingerprint-to-system hashmap
    """
    def __init__(self, systems):
        self.fps = {}
        for sys in systems:
            for fp in sys.fingerprints:
                self.fps[fp] = sys

    def get_system(self, fingerprint):
        if fingerprint not in self.fps:
            return None

        return self.fps[fingerprint]
