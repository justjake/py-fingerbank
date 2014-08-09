# py-fingerbank

A [fingerbank](http://www.fingerbank.org/) support library for Python 2.6 and above.

(c) 2014 Jake Teton-Landis.

LGPL terms.

## Progress

We have a parser for the `dhcp_fingerprints.conf` file in fingerbank's repo,
and a few classes for representing operating systems and groups thereof.
Most of the heaving lifting happens in `parser.py`, which creates python
ConfigParser objects from the perl .conf file, and then builds objects from the
python conf.

You can convert `dhcp_fingerprints.conf` to a python config pretty easily with
my parser:

```python
from fingerbank.parser import parse_config_with_heredocs
cfg = parse_config_with_heredocs('data/dhcp_fingerprints.conf')
with open('py_fingerprints.conf', 'wb') as f:
    cfg.write(f)
```

Of course, that removes comments and stuff, but it's a nice testcase!
