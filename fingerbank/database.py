"""A database of DHCP fingerprints"""
from collections import defaultdict


class HashTree(object):
    """a dictionary structure made of a tree of HashTrees"""
    def __init__(self, value=None):
        self.subtree = {}
        self.value = value

    def __str__(self):
        return '<HashTree {0}, {1}>'.format(
            repr(self.value), repr(self.subtree))

    def __repr__(self):
        return str(self)

    def put(self, path, value):
        """
        put a value at a given path
        :param path: list of keys
        :param value: the value to store
        >>> ht = HashTree()
        >>> ht.put([1,2,3], "hello")
        """
        if len(path) == 0:
            self.value = value
            return

        # put it into child
        first = path[0]
        rest = path[1:]
        # create children if needed
        if first not in self.subtree:
            self.subtree[first] = HashTree()
        self.subtree[first].put(rest, value)

    def get(self, path):
        """
        retrieve a value from a given path
        :param path: list of keys
        >>> ht = HashTree()
        >>> ht.put([1,2,3], "hello")
        >>> ht.get([1,2,3])
        "hello"
        """
        if len(path) == 0:
            return self.value

        return self.subtree[path[0]].get(path[1:])


class DummyHashTree(object):
    """implements HashTree's interface using a normal map"""
    def __init__(self):
        self.vals = {}

    def put(self, path, value):
        path = ','.join(path)
        self.vals[path] = value

    def get(self, path):
        path = ','.join(path)
        if path not in self.vals:
            return None
        return self.vals[path]


class Group(object):
    """
    a group of systems in fingerbank's conf.
    the conf has groups with multiple ranges, but we don't support those yet.
    """
    def __init__(self, num, desc, start, end):
        self.number = int(num)
        self.description = desc
        self.start = int(start)
        self.end = int(end)

    def __repr__(self):
        return 'Group({num}, {desc}, {start}, {end})'.format(
            num=repr(self.number),
            desc=repr(self.description),
            start=repr(self.start),
            end=repr(self.end))


class System(object):
    """an operating system with a bunch of DHCP fingerprints"""
    def __init__(self, num, desc, fprints, vendor=None):
        self.number = int(num)
        self.description = desc

        if isinstance(fprints, str):
            fprints = fprints.split('\n')
        self.fingerprints = fprints
        self.vendor_id = vendor

    def __repr__(self):
        return 'System({num}, {desc})'.format(
            num=repr(self.number), desc=repr(self.description))


class Database(object):
    """
    fast lookups for fingerprints.
    I'm not sure this implementation is very good; I'm still toying with it.
    I may go for a straight-up port of fingerbank's tools instead.
    """
    def __init__(self, systems=None, groups=None):
        self.vendors = defaultdict(lambda: set())
        self.fp_lookup = DummyHashTree()
        self.systems = {}
        self.groups = {}

        if systems:
            for sys in systems:
                self.add_system(sys)

        if groups:
            for g in groups:
                self.add_group(g)

    def exact_match(self, fingerprint):
        """
        return the operating system for a given fingerprint
        """
        if isinstance(fingerprint, str):
            fingerprint = fingerprint.split(',')

        return self.fp_lookup.get(fingerprint)

    def add_system(self, system):
        # add to vendor grouping if we have one
        if system.vendor_id:
            self.vendors[system.vendor_id].add(system)

        # insert into path by each fingerprint (not sure if it works like dis)?
        for fp in system.fingerprints:
            path = fp.split(',')
            self.fp_lookup.put(path, system)

        self.systems[system.number] = system

    def add_group(self, group):
        self.groups[group.number] = group

    def get_group_for_system(self, system):
        """
        given a system, retrieve it's group
        """
        def f(group):
            return group.start <= system.number and group.end >= system.number
        candidates = filter(f, self.systems.values())
        if len(candidates):
            return candidates[0]
        return None
