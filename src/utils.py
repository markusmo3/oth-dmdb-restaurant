from collections import defaultdict
from typing import List, Any, Set, Tuple, Iterable

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


def loadGoldStandard() -> Tuple[List[Set[int]], List[int]]:
    """Loads the Gold Standard from the file provided by the HPI 'restaurants_DPL.tsv'

    Returns:
        a tuple with two lists (dupeSets, dupeIds).
            dupeSets is a list of all rows in the Gold Standard as sets
            dupeIds is a list of all ids that are in Gold Standard
    """
    dupeDf = pd.read_csv(PATH_PREFIX + '/restaurants_DPL.tsv', delimiter='\t')
    dupeDict = {}
    for i, dupeRow in dupeDf.iterrows():
        if dupeRow[0] not in dupeDict:
            dupeDict[dupeRow[0]] = set()
            dupeDict[dupeRow[0]].add(dupeRow[0])
        dupeDict[dupeRow[0]].add(dupeRow[1])

    dupeSets: List[Set[Any]] = list(dupeDict.values())
    dupeIds: List[int] = [y for x in dupeSets for y in x]
    return dupeSets, dupeIds


def compareDfToGold(df: pd.DataFrame, total=864) -> Tuple[Set, Set, Set, List]:
    return compareToGold(list(df[df.id.map(len) > 1].id), total)


def compareToGold(duplicates: List[Set[int]], total=864, printType="table") -> Tuple[Set, Set, Set, List]:
    """Compares the given list of duplicates to the Gold Standard and prints and returns the results

    Args:
        duplicates: to compare to the Gold Standard
        total: the total number of records
        printType: the type in which this method should print its results
            (possible values: "table", "csv", or anything else to not print at all)

    Returns:
        A Tuple (true_positive, false_negative, false_positive, listOfParams)
    """
    recognizedDuplicates = duplicates
    true_positive = set()
    false_negative = set()
    false_positive = set()
    for dupeSet in GOLD_DUPE_SETS:
        if dupeSet in recognizedDuplicates:
            true_positive.add(frozenset(dupeSet))
        else:
            false_negative.add(frozenset(dupeSet))
    for recognizedDupeSet in recognizedDuplicates:
        if recognizedDupeSet in GOLD_DUPE_SETS:
            true_positive.add(frozenset(recognizedDupeSet))
        else:
            false_positive.add(frozenset(recognizedDupeSet))

    # times 2 because we work with sets of 2
    fn = len([e for s in false_negative for e in s])
    fp = len([e for s in false_positive for e in s])
    tp = len([e for s in true_positive for e in s])
    tn = total - tp - fn - fp
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    fScore = (2 * precision * recall) / (precision + recall)
    listOfParams = [tp, tn, fp, fn, precision, recall, fScore]
    if printType == "table":
        print("tp={:<5}, tn={:<5}, fp={:<5}, fn={:<5}, precision={:< .3f}, recall={:< .3f}, fScore={:< .3f}"
              .format(*listOfParams))
    elif printType == "csv":
        print(*listOfParams, sep=",")
    return true_positive, false_negative, false_positive, listOfParams


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
          + PATH_PREFIX + "'.")
    print("You can use those with mongoimport!")
    print("Example:")
    print("  mongoimport [...] --db dmdb --collection clean --type json --file deduped_raw.json -v --jsonArray --drop")
    return df


def difference(li1: List[Any], li2: List[Any]) -> Tuple[List[Any], List[Any]]:
    left = [i for i in li1 + li2 if i not in li1]
    right = [i for i in li1 + li2 if i not in li2]
    return left, right


PATH_PREFIX = "../data/work"
GOLD_DUPE_SETS, GOLD_DUPE_IDS = loadGoldStandard()
config = {
    # if True a comparison to the gold standard will be made
    "compareToGold": True,
    # if True then the results of the deplucation will be prepared and saved as json files
    # to enable an import into mongodb
    "prepareUploadJsons": True,

    # this is a feature flag to toggle the old way on, that found all but 12 duplicates
    # if this is set to false a slightly improved way is used, which found all but 8 duplicates
    # ONLY applies when the clean.py is used
    "useOldCalculation": False
}
