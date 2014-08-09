"""Parser for the fingerbank config file format"""
import ConfigParser
import re
import logging

from fingerbank.database import System, Group

EMPTY = re.compile(r'\s*\n')
COMMENT = re.compile(r'^\s*#')
SECTION = re.compile(r'^\s*\[([^\]]+)\]')
SET_HEREDOC = re.compile(r'^(\w+)\s*=\s*<<(\w+)$')
SET_VALUE = re.compile(r'^(\w+)\s*=\s*([^\n#]+)')
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


def parse_config_with_heredocs(fn):
    """
    load the given filename into a python config object
    :param fn: filename to open and parse
    :returns RawConfigParser:
    """
    lines = open(fn).readlines()
    cfg = ConfigParser.RawConfigParser()

    section = 'DEFAULT'
    key = None
    heredoc_eof = None
    heredoc_data = []

    for line in lines:
        logging.debug("LINE: {0}".format(repr(line)))
        # heredoc handling comes first
        if heredoc_eof:
            logging.debug("\tin heredoc. key = '{key}', EOF = '{eof}'".format(
                key=key, eof=heredoc_eof))
            # end heredoc, add to section
            if line == heredoc_eof + "\n":
                logging.debug('\tfinished heredoc.')
                cfg.set(section, key, ''.join(heredoc_data))
                key = None
                heredoc_data = []
                heredoc_eof = None
                continue

            # otherwise just add current line value to heredoc data so far
            heredoc_data.append(line)
            continue

        # not in a heredoc! what can we have on line?
        # skip empty lines
        if EMPTY.match(line):
            logging.debug('\tempty')
            continue

        # skip comments
        if COMMENT.match(line):
            logging.debug('\tcomment')
            continue

        # enter sections
        if SECTION.match(line):
            m = SECTION.match(line)
            section = m.group(1)
            cfg.add_section(section)
            logging.debug('\tsection {0}'.format(repr(section)))
            continue

        # begin heredocs
        if SET_HEREDOC.match(line):
            logging.debug('\topening heredoc')
            m = SET_HEREDOC.match(line)
            key = m.group(1)
            heredoc_eof = m.group(2)
            continue

        # parse normal key=values
        if SET_VALUE.match(line):
            m = SET_VALUE.match(line)
            key = m.group(1)
            value = m.group(2)
            cfg.set(section, key, value)
            logging.debug('\tsetting [{s}].{k} <-- {v}'.format(
                s=section, k=key, v=repr(value)))
            continue

        # other things are a problem!!!!
        raise ValueError('Unexpected line: {0}'.format(line))

    return cfg

OS = re.compile(r'os (\d+)')
GROUP = re.compile(r'class (\d+)')

DESC = 'description'
FINGERPRINTS = 'fingerprints'
VENDOR = 'vendor_id'
MEMBERS = 'members'


def _build_system(cfg, section_name):
    n = OS.match(section_name).group(1)
    desc = cfg.get(section_name, DESC)
    f = cfg.get(section_name, FINGERPRINTS)
    v = None
    if cfg.has_option(section_name, VENDOR):
        v = cfg.get(section_name, VENDOR)
    return System(n, desc, f, v)


def _build_group(cfg, section_name):
    n = GROUP.match(section_name).group(1)
    desc = cfg.get(section_name, DESC)
    mems = cfg.get(section_name, MEMBERS)
    ranges = mems.split(',')
    # TODO: handle more than one range
    start, end = ranges[0].split('-')
    return Group(n, desc, start, end)


def create_systems_and_groups(cfg):
    """
    create systems and groups from a ConfigParser containing
    Fingerbank information
    :returns: list of systems, list of groups
    """
    groups = []
    systems = []
    for sect in cfg.sections():
        if OS.match(sect):
            try:
                systems.append(_build_system(cfg, sect))
            except ConfigParser.NoOptionError:
                pass
            continue

        if GROUP.match(sect):
            groups.append(_build_group(cfg, sect))
            continue

    return systems, groups
