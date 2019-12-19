from typing import List, Any, Set, Tuple

import pandas as pd
import textdistance as td
import numpy as np
import json
from itertools import combinations
from src.utils import merge_common

PATH_PREFIX = "../data/work"
READ_FROM_FILE = True
DO_BIAS = True


def calcDistances(strings: Set[str], completelyInsideOtherBias: float = 0.5) -> List[Tuple[str, str, float]]:
    def bias(s1, s2):
        if s1 in s2 or s2 in s1:
            return completelyInsideOtherBias
        else:
            return 0

    stringCombinations = set(map(frozenset, combinations(set(strings), 2)))

    allDistances = []
    if READ_FROM_FILE:
        with open(PATH_PREFIX + "/jaccard.json", "r") as file:
            allDistances = json.loads(file.read())
    else:
        allDistances = [(s1, s2, s1 == s2 and -1 or td.jaccard(s1, s2)) for s1, s2 in stringCombinations]
        allDistances.sort(key=lambda x: x[2], reverse=True)
        with open(PATH_PREFIX + "/jaccard.json", "w+") as file:
            file.write(json.dumps(allDistances))

    if DO_BIAS:
        for i in range(len(allDistances)):
            allDistances[i][2] = allDistances[i][2] + bias(allDistances[i][0], allDistances[i][1])
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

    # times 2 because we work with sets of 2
    tp = len(true_positive) * 2
    fn = len(false_negative) * 2
    fp = len(false_positive) * 2
    print("True positives: " + str(tp))
    print("False negatives: " + str(fn))
    print("False positives: " + str(fp))
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    fscore = (2 * precision * recall) / (precision + recall)
    print("Precision: " + str(precision))
    print("Recall: " + str(recall))
    print("Fscore: " + str(fscore))
    return true_positive, false_negative, false_positive


def __findClosestEqRingMatch(eqRing, searchString):
    for ring in eqRing:
        for e in ring:
            if e == searchString:
                return ring[0]
    return searchString


def dedupe(df, eqRing):
    df["tdkey"] = df.cname.copy()
    df["tdkey"] = df["tdkey"].apply(lambda s: __findClosestEqRingMatch(eqRing, s))
    df = df.groupby(["phone", "tdkey"]).agg(set).reset_index()
    return df


def clean(df, completelyInsideOtherBias=0.5, filterCutoff=0.7):
    df = preProcess(df)
    distances = calcDistances(df.cname.unique(), completelyInsideOtherBias)
    filteredDistances = list(filter(lambda x: x[2] >= filterCutoff, distances))
    eqRing = convertToEqualityRings(filteredDistances)
    return dedupe(df, eqRing)


if __name__ == '__main__':
    dupesets, dupeids = loadGoldStandard()
    dataframe = pd.read_csv(PATH_PREFIX + '/restaurants.tsv', delimiter='\t')
    cleaned = clean(dataframe, 0.7, 0.7)
    compareToGold(cleaned, dupesets)
