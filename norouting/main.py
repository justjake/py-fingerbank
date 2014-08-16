from fingerbank.parser import (parse_config_with_heredocs,
        create_systems_and_groups, _build_group)
from fingerbank.match import (
        Test, Matcher, 
        largest_common_subsequence, top_5,
        format_results)

ROUTERS = 'class 4'

def main(cfg_file, fp):
    cfg = parse_config_with_heredocs(cfg_file)
    router = _build_group(cfg, ROUTERS)

    # reducer
    def top_5_routers(results):
        return top_5(r for r in results if router.includes(r.system))

    # full test
    router_ratio = Test('LCS of routers', largest_common_subsequence, top_5_routers)

    # all the data
    systems, groups = create_systems_and_groups(cfg)
    matcher = Matcher(systems, [router_ratio])
    print matcher.match(fp).format()
