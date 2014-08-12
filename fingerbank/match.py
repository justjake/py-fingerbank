"""
python implementation of tools/fingerprint-find-candidate-matches.pl

Find what fingerprint matches the most a given DHCP fingerprint.
Supports several strategies to do so and adding new ones should be relatively easy.
"""

from fingerbank.parser import (
        FINGERPRINTS, _build_system, parse_config_with_heredocs,
        create_systems_and_groups
        )

class Test(object):
    name = 'test'
    description = 'always returns None for everything because this is baseclass'

    def __init__(self):
        self.results = None

    def run(self, fp_to_match, fp):
        """
        test to see if fp somehow relates to fp_to_match
        """
        return None

    def filter_results(self, results):
        """
        given a hash of all results data, return just the systems or fingerprints
        that we care about.

        Results is a hash like this:
        {
            # one of these for each fingerprint (!)
            '1,2,3,4,5' -> {
                'system' -> <System object>
                'test_name' -> result of test_name.run()
                'test_name_2' -> result of test_name_2()
            },
            ...
        }
        """
        return None

# this is a little java-y
# blarg
class Matcher(object):
    def __init__(self, systems):
        self.systems = systems

    def process(self, fp_to_match, tests):
        for system in self.systems:
            # for each of the fingerprints, run each check
            for fp in system.fingerprints:
                results[fp] = dict(system=system)
                for test in tests:
                    results[fp][test.name] = test.run(fp_to_match, fp)

    def gather_results(self, results, tests):
        per_test_results = {}
        for test in tests:
            per_test_results[test] = test.filter_results(results)
        return per_test_results

def main(conf_file_name, fp_to_match):
    cfg = parse_config_with_heredocs(conf_file_name)
    systems, _ = create_systems_and_groups(cfg)
    matcher = Matcher(systems)
    tests = [ Test() ]

    raw_results = matcher.process(fp_to_match, tests)
    per_test_result = matcher.gather_results(raw_results, tests)

    for test in tests:
       print("\nTest: {test} results".format(test=test.name))
       print("Description: {desc}".format(desc=test.description))

       if not (per_test_result[test]):
           print "No results..."
           continue

       # TODO: rework to have the actual fingerprint
       # TODO: rewrite everything to make it actually make sense
       #       and not be hella convoluted
       for res in per_test_result[test]:
           sys = res['system']
           print("{os_desc} (os {num}): {fp}\n{res}".format(
               os_desc=sys.description,
               num=sys.num,
               fp='oops need to index by fingerprints',
               res='nah'))
