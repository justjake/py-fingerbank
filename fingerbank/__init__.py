"""
Fingerbank tools.
Usage:
    >>> import fingerbank
    >>> oses, groups = fingerbank.read('data/dhcp_fingerprints.conf')

then implement your own filtering and selection on top of those nifty
values. More tools forthcoming in other modules
"""

from .parser import create_systems_and_groups, parse_config_with_heredocs
from .database import System, Group


def read(fn):
    """
    return a list of the operating systems and a list of the groups in
    the given fingerbank config file
    """
    cfg = parse_config_with_heredocs(fn)
    return create_systems_and_groups(cfg)
