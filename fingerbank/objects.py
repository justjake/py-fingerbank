"""
classical representations of the things you find in the fingerbank conf file
"""

class Group(object):
    """
    a group of systems in fingerbank's conf.
    the conf has groups with multiple ranges, but we don't support those yet.
    """
    def __init__(self, num, desc, ranges):
        """
        :param num: conf group ID number in the conf file. int.
        :param desc: description of this group. str.
        :param ranges: list of (start :: int, end :: int) tuples describing
            what machine numbers are in this group. Many groups have only
            one range, but some have more. Ranges are inclusive.
            Example: `[(1, 199), (1200, 1250), (76, 76)]`
        """
        self.number = int(num)
        self.description = desc
        self.ranges = ranges

    def __repr__(self):
        return 'Group({num}, {desc}, {start}, {end})'.format(
            num=repr(self.number),
            desc=repr(self.description),
            start=repr(self.start),
            end=repr(self.end))

    def includes(self, system):
        """
        true if this group contains that system
        """
        return any(start <= system.number and end >= system.number
                for start, end in self.ranges)


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
