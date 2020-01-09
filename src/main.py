from itertools import combinations
from typing import List, Set, Tuple

import pandas as pd
import textdistance as td

import utils


class Regexes:
    """
    Class that contains all regular expressions used in the data pre processing.
    """
    CITY_REPLACE_DICT = {
        r"w. hollywood": "west hollywood",
        r"new york city": "new york",
        r"west la": "los angeles",
        r"la": "los angeles"
    }
    ADDRESS_REPLACE_DICT = {
        r"(ave|av)": "ave",
        r"(blvd|blv)": "blvd",
        r"(sts)": "st",
        r"s\.": "s",
        r" ?between.*$": ""
    }
    TYPE_REMOVE_REGEX = r"^.*[0-9] ?"
    BRACKETS_REGEX = r" ?\(.*\)"
    NON_ALPHA_OR_SPACE_REGEX = r"[^a-zA-Z0-9 ]"
    NON_ALPHA_REGEX = r"[^a-zA-Z0-9]"


def preProcess(df: pd.DataFrame) -> pd.DataFrame:
    """Pre processes the given DataFrame by applying a lot of Regex replacements.

    Args:
        df: a pandas DataFrame to pre process

    Returns:
        a pre processed pandas DataFrame
    """

    for k, v in Regexes.ADDRESS_REPLACE_DICT.items():
        df.address = df.address.str.replace(k, v, case=False, regex=True)
    for k, v in Regexes.CITY_REPLACE_DICT.items():
        df.city = df.city.str.replace(k, v, case=False, regex=True)
    df.type = df.type.fillna("")
    df.type = df.type.str.replace(Regexes.BRACKETS_REGEX, '', case=False) \
        .str.replace(Regexes.TYPE_REMOVE_REGEX, "", case=False)
    df.phone = df.phone.str.replace(Regexes.NON_ALPHA_REGEX, '', case=False)
    df.name = df.name.str.replace(Regexes.BRACKETS_REGEX, '', case=False)

    df["cname"] = df.name.copy()
    df["caddress"] = df.address.copy()
    df.cname = df.cname.str.replace(Regexes.NON_ALPHA_OR_SPACE_REGEX, '', case=False) \
        .str.replace('  the$', '', case=False)
    df.caddress = df.caddress.str.replace(Regexes.NON_ALPHA_OR_SPACE_REGEX, '', case=False)
    return df


def areRowsSame(r1, r2, distanceAlgorithm=td.jaccard, minTokenDistance=0.5, minTextDistance=0.9) -> bool:
    """Compares the two rows row1 and row2, if they are the same

    Args:
        r1: to compare
        r2: to compare
        distanceAlgorithm: to use, default td.jaccard
        minTokenDistance: to use, default 0.5
        minTextDistance: to use, default 0.9

    Returns:
        True if they should be considered the same, or False otherwise
    """

    def stringsSimilar(s1: str, s2: str) -> bool:
        return distanceAlgorithm(s1.split(), s2.split()) >= minTokenDistance \
               or distanceAlgorithm(s1, s2) >= minTextDistance

    def numbersEqual(s1: str, s2: str) -> bool:
        ints1 = [int(s) for s in s1.split() if s.isdigit()]
        ints2 = [int(s) for s in s2.split() if s.isdigit()]
        return ints1 == ints2

    if r1.phone == r2.phone:
        return stringsSimilar(r1.cname, r2.cname) \
               or r1.cname in r2.cname \
               or r2.cname in r1.cname
    if r1.city == r2.city:
        return stringsSimilar(r1.cname, r2.cname) \
               and stringsSimilar(r1.caddress, r2.caddress) \
               and numbersEqual(r1.caddress, r2.caddress)
    else:
        return False


def deduplicate(df: pd.DataFrame, distanceAlgorithm=td.jaccard, minTokenDistance=0.5, minTextDistance=0.9) \
        -> Tuple[pd.DataFrame, List[Set[int]]]:
    """Deduplicates the given pandas DataFrame completely

    Args:
        df: a fresh pandas DataFrame
        distanceAlgorithm: to use, default td.jaccard
        minTokenDistance: to use, default 0.5
        minTextDistance: to use, default 0.9

    Returns:
        a tuple of (df: DataFrame, recognizedDupeSets: List[Set[int]]).
            df is the cleaned DataFrame, grouped and aggregated.
            recognizedDupeSets is a list of sets that contain the ids.
    """
    df = preProcess(df)
    recognizedDupeSets = []
    for twoRows in combinations(df.itertuples(), 2):
        row1 = twoRows[0]
        row2 = twoRows[1]
        if areRowsSame(row1, row2, distanceAlgorithm, minTokenDistance, minTextDistance):
            recognizedDupeSets.append({row1.id, row2.id})

    # merge common elements, isn't needed, but to make it future-proof
    mergedDupeSets = list(utils.merge_common(recognizedDupeSets))
    # convert back to a list of sets
    mergedDupeSets = list(map(lambda x: set(x), mergedDupeSets))

    # give every row a unique negative identifier
    df["group"] = df["id"].copy().apply(lambda x: -x)
    for idx, dupeset in enumerate(mergedDupeSets):
        # assign each set of duplicates a new unique positive identifier
        for di in dupeset:
            df.at[di-1, "group"] = idx

    # group by the identifier
    df = df.groupby(["group"]).agg(set).reset_index()
    return df, mergedDupeSets


def simpleCompareToGold(dupes):
    dupeSets, dupeIds = utils.loadGoldStandard()
    print("Real duplicates: ", dupeSets)
    print("Found duplicates:", dupes)
    fn, fp = utils.difference(dupes, dupeSets)
    print("False negatives:", len(fn), fn)
    print("False positives:", len(fp), fp)


if __name__ == '__main__':
    originalDf = pd.read_csv(utils.PATH_PREFIX + '/restaurants.tsv', delimiter='\t')
    cleaned, dupes = deduplicate(originalDf)

    if utils.config["compareToGold"]:
        print("tp,tn,fp,fn,precision,recall,fscore")
        utils.compareToGold(dupes, printType="csv")

    if utils.config["prepareUploadJsons"]:
        utils.prepareUploadJsons(cleaned)

    # simpleCompareToGold(dupes)
