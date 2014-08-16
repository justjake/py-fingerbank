"""
python implementation of tools/fingerprint-find-candidate-matches.pl

Find what fingerprint matches the most a given DHCP fingerprint.
Supports several strategies to do so and adding new ones should be relatively easy.
"""

from fingerbank.parser import (
        parse_config_with_heredocs, create_systems_and_groups)

from difflib import SequenceMatcher
from collections import namedtuple
from timeit import timeit


class Test(namedtuple('Test', 'desc compare reduce')):
    """
    Use the Test class to group comparison functions with reduce functions.
    The comparison function compares two fingerprints and returns some assesment
    of how similar they are.

    The reduce function takes an iterable of Result tuples (system,
    fingerprint, comparison result) and returns a list of only the interesting
    results. The simplest possible reduce function is `list`
    """
    pass


class Result(namedtuple('Result', 'system fingerprint value')):
    def _for_test(self, some_test):
        """
        by convention the `value` member is a hash from test -> comparison result.
        this function returns a Result with just the comparison result for the
        given test.
        """
        return Result(self.system, self.fingerprint, self.value[some_test])

# this is a little java-y
# blarg
class Matcher(object):
    def __init__(self, systems, tests):
        self.systems = systems
        self.tests = tests

    def match(self, fp_to_match):
        """
        matches fp against all the fingerprints in this matcher's systems using
        the tests.
        :param fp_to_match: string. DHCP options fingerprint
        :param tests: list of comparason functions. These functions take two
            values and return some assessment of the similarity, which can be
            anything.
        """
        results = []
        for system in self.systems:
            # for each of the fingerprints, run each check
            for fp in system.fingerprints:
                res = Result(system, fp, {})
                results.append(res)
                # store the check result keyed to the check
                for test in self.tests:
                    res.value[test] = test.compare(fp_to_match, fp)
        self.results = results
        return results

    def reduce(self, results=None):
        results = results or self.results
        final = []
        for test in self.tests:
            final.append((test.desc, 
                test.reduce(r._for_test(test) for r in results)
                ))
        return final


def option_set(fp):
    """set of all the options in a fingerprint"""
    return set(fp.split(','))


def count_identical_matches(a, b):
    """
    returns the number of options both a and b share
    :param a: comma seperated fingerprint
    :param b: comma seperated fingerprint
    """
    a = option_set(a)
    b = option_set(b)
    return len(a & b) # & is intersecion


def perfect_match(a, b):
    """
    returns true if a and b are a perfect match
    :param a: comma seperated fingerprint
    :param b: comma seperated fingerprint
    """
    return a == b


def largest_common_subsequence(a, b, worth_considering=0.5):
    """
    returns a ratio between 0..1 of how similar two fingerprints are.
    because actually computing the subsequenes can be very slow, we do some
    quick ratio bound checking to make sure it wasn't shit

    :param a: comma seperated fingerprint
    :param b: comma seperated fingerprint
    """
    a, b = a.split(','), b.split(',')
    sm = SequenceMatcher(lambda x: x == '\n', a, b)
    upper_bound = sm.quick_ratio()
    if upper_bound >= worth_considering:
        return sm.ratio()
    return upper_bound


def top_5(results):
    """
    return the top 5 results as sorted by python
    """
    return sorted(results, reverse=True, key=lambda r: r.value)[0:4]


def all_true(results):
    """
    return all results with true values
    """
    return filter(lambda r: r.value, results)


def return_all(results):
    """
    just return everything
    """
    return list(results)


def main(conf_file_name, fp_to_match):
    cfg = parse_config_with_heredocs(conf_file_name)
    systems, _ = create_systems_and_groups(cfg)
    
    similarity_ratio = Test('Similarity', largest_common_subsequence, top_5)
    exact_matches = Test('All exact matches', perfect_match, all_true)
    same_options = Test('Fingerprints with matching options',
            count_identical_matches, top_5)
    
    tests = [exact_matches, similarity_ratio, same_options]
    matcher = Matcher(systems, tests)

    print("Fingerprint: {0}".format(fp_to_match))

    reduced = []
    def do_things():
        raw_results = matcher.match(fp_to_match)
        reduced.append(matcher.reduce(raw_results))

    t = timeit(do_things, number=1)
    reduced = reduced[0]
    print("matching {sys} systems with {tests} tests took {t} seconds".format(
        sys=len(systems),
        tests=len(tests),
        t=t))

    for test, results in reduced:
        print("\nTest: {0} vs {1}".format(test, fp_to_match))
        if not results:
            print("No results...")
            continue

        for r in results:
           print("{os_desc} (os {num}): {fp}\n    {res}".format(
               os_desc=r.system.description,
               num=r.system.number,
               fp=r.fingerprint,
               res=r.value))

if __name__ == '__main__':
    import sys
    main(sys.argv[1], sys.argv[2])
