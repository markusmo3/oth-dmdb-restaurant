from typing import List, Any, Set, Tuple

import pandas as pd
import textdistance as td
from itertools import combinations
from src.utils import merge_common

PATH_PREFIX = "../data/work"


def calcDistances(strings: Set[str], completelyInsideOtherBias: float = 0.5) -> List[Tuple[str, str, float]]:
    def bias(s1, s2):
        if s1 in s2 or s2 in s1:
            return completelyInsideOtherBias
        else:
            return 0

    stringCombinations = set(map(frozenset, combinations(set(strings), 2)))
    allDistances = [(s1, s2, s1 == s2 and -1 or td.jaccard(s1, s2) + bias(s1, s2)) for s1, s2 in stringCombinations]
    allDistances.sort(key=lambda x: x[2], reverse=True)
    return allDistances


def convertToEqualityRings(distanceList: List[Tuple[str, str, float]]) -> List[Set[str]]:
    sets = map(lambda x: set(x[0:2]), distanceList)
    return list(merge_common(sets))


def loadGoldStandard() -> Tuple[List[set], List[int]]:
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


class Statics:
    CITY_REPLACE_DICT = {
        "w. hollywood": "west hollywood",
        "new york city": "new york",
        "west la": "los angeles",
        "la": "los angeles"
    }
    ADDRESS_REPLACE_DICT = {
        r"(ave|av)": "ave",
        r"(blvd|blv)": "blvd",
        r"(sts)": "st",
        r"s\.": "s",
        r" ?between.*$": ""
    }
    BRACKETS_REGEX = r" ?\(.*\)"
    NON_ALPHA_OR_SPACE_REGEX = r"[^a-zA-Z0-9 ]"
    NON_ALPHA_REGEX = r"[^a-zA-Z0-9]"


def preProcess(df):
    # reformat the index
    # df = df.drop(labels=['id'], axis=1)
    # df.set_index("id", inplace=True)

    for k, v in Statics.ADDRESS_REPLACE_DICT.items():
        df.address = df.address.str.replace(k, v, case=False, regex=True)
    for k, v in Statics.CITY_REPLACE_DICT.items():
        df.city = df.city.str.replace(k, v, case=False)
    df.type = df.type.fillna("")
    df.type = df.type.str.replace(Statics.BRACKETS_REGEX, '', case=False) \
        .str.replace(r"^.*[0-9] ?", "", case=False)
    df.phone = df.phone.str.replace(Statics.NON_ALPHA_REGEX, '', case=False)
    df.name = df.name.str.replace(Statics.BRACKETS_REGEX, '', case=False)

    df["cname"] = df.name.copy()
    df["caddress"] = df.address.copy()
    df.cname = df.cname.str.replace(Statics.NON_ALPHA_OR_SPACE_REGEX, '', case=False) \
        .str.replace('  the$', '', case=False)
    df.caddress = df.caddress.str.replace(Statics.NON_ALPHA_OR_SPACE_REGEX, '', case=False)
    return df


def compareToGold(df, dupesets):
    recognizedDuplicates = list(df[df.id.map(len) > 1].id)
    true_positive = []
    false_negative = []
    false_positive = []
    for dupeset in dupesets:
        if dupeset in recognizedDuplicates:
            true_positive.append(dupeset)
        else:
            false_negative.append(dupeset)
    for recset in recognizedDuplicates:
        if recset not in dupesets:
            false_positive.append(recset)
    print("True positives: " + str(len(true_positive)))
    print("False negatives: " + str(len(false_negative)))
    print("False positives: " + str(len(false_positive)))
    precision = len(true_positive) / (len(true_positive) + len(false_positive))
    recall = len(true_positive) / (len(true_positive) + len(false_negative))
    fscore = (2 * precision * recall) / (precision + recall)
    print("Precision: " + str(precision))
    print("Recall: " + str(recall))
    print("Fscore: " + str(fscore))
    return true_positive, false_negative, false_positive


def dedupe(df, eqRing):
    df["tdkey"] = df.cname.copy()
    df.tdkey = df.tdkey.apply(lambda s: __findClosestEqRingMatch(eqRing, s))
    df = df.groupby(["phone", "tdkey"]).agg(set).reset_index()
    return df


def __findClosestEqRingMatch(eqRing, searchString):
    for ring in eqRing:
        for e in ring:
            if e == searchString:
                return ring[0]
    return searchString


def clean(df, completelyInsideOtherBias=0.5, filterCutoff=0.7):
    df = preProcess(df)
    distances = calcDistances(df.cname.unique(), completelyInsideOtherBias)
    filteredDistances = list(filter(lambda x: x[2] >= filterCutoff, distances))
    eqRing = convertToEqualityRings(filteredDistances)
    return dedupe(df, eqRing)


if __name__ == '__main__':
    dupesets, dupeids = loadGoldStandard()
    df = pd.read_csv(PATH_PREFIX + '/restaurants.tsv', delimiter='\t')
    cleaned = clean(df, 0.7, 0.7)
    compareToGold(cleaned, dupesets)
