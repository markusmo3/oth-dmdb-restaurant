from typing import List, Any, Set, Tuple, Iterator, Iterable
from collections import defaultdict
import pandas as pd

PATH_PREFIX = "../data/work"

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


def loadGoldStandard() -> Tuple[List[Set[int]], List[int]]:
    """Loads the Gold Standard from the file provided by the HPI 'restaurants_DPL.tsv'

    Returns:
        a tuple with two lists (dupesets, dupeids).
            dupesets is a list of all rows in the Gold Standard as sets
            dupeids is a list of all ids that are in Gold Standard
    """
    dupedf = pd.read_csv(PATH_PREFIX + '/restaurants_DPL.tsv', delimiter='\t')
    dupedict = {}
    for i, dupeRow in dupedf.iterrows():
        if dupeRow[0] not in dupedict:
            dupedict[dupeRow[0]] = set()
            dupedict[dupeRow[0]].add(dupeRow[0])
        # dupedict[dupeRow[0]].add(dupeRow[0])
        dupedict[dupeRow[0]].add(dupeRow[1])

    dupesets: List[Set[Any]] = list(dupedict.values())
    dupeids: List[int] = [y for x in dupesets for y in x]
    return dupesets, dupeids


def prepareUploadJsons(df: pd.DataFrame) -> pd.DataFrame:
    """Prepares and saves two json files that can be imported into mongodb.
        Look in ../data/work/deduped_raw.json and ../data/work/deduped_clean.json

    Args:
        df: a pandas DataFrame

    Returns:
        a pandas DataFrame
    """
    def __firstOfSet(s: Any) -> Any:
        if isinstance(s, set):
            return s.pop()
        else:
            return s

    if "group" in df:
        df.drop("group", axis=1, inplace=True)
    df.to_json(PATH_PREFIX + '/deduped_raw.json', orient='records')
    df.name = df.name.apply(__firstOfSet)
    df.address = df.address.apply(__firstOfSet)
    df.city = df.city.apply(__firstOfSet)
    df.cname = df.cname.apply(__firstOfSet)
    df.caddress = df.caddress.apply(__firstOfSet)
    df.to_json(PATH_PREFIX + '/deduped_clean.json', orient='records')
    print("Written two jsons 'deduped_raw.json' and 'deduped_clean.json' to directory '"
          + PATH_PREFIX + "'.\nYou can use those with mongoimport!")
    return df



def difference(li1, li2):
    left = [i for i in li1 + li2 if i not in li1]
    right = [i for i in li1 + li2 if i not in li2]
    return left, right