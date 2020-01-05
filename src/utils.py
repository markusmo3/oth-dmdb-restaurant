from typing import List, Any, Set, Tuple, Iterator, Iterable
from collections import defaultdict
import pandas as pd


def printUniqueTokens(series: pd.Series):
    unique_series = series.unique()
    token_count = {}
    for a in unique_series:
        tokens = a.split(' ')
        for t in tokens:
            if t not in token_count:
                token_count[t] = 1
            else:
                token_count[t] += 1

    for key, value in sorted(token_count.items(), key=lambda item: item[1]):
        print("%s: %s" % (key, value))


# Source: https://www.geeksforgeeks.org/python-merge-list-with-common-elements-in-a-list-of-lists/
# merge function to merge all sublist having common elements.
def merge_common(lists: Iterable[Iterable[Any]]) -> List[List[Any]]:
    neigh = defaultdict(set)
    visited = set()
    for each in lists:
        for item in each:
            neigh[item].update(each)

    def comp(node, neigh=neigh, visited=visited, vis=visited.add):
        nodes = {node}
        next_node = nodes.pop
        while nodes:
            node = next_node()
            vis(node)
            nodes |= neigh[node] - visited
            yield node

    for node in neigh:
        if node not in visited:
            yield sorted(comp(node))
