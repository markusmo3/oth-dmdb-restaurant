from typing import List, Any, Set, Tuple

import pandas as pd
import textdistance as td
import json
from itertools import combinations
from src.utils import merge_common


def calcDistances(strings: Set[str], completelyInsideOtherBias: float = 0.7,
                  algo: str = "jaccard", readFromFile: bool = True, writeToFile: bool = True, doBias: bool = True)\
        -> List[Tuple[str, str, float]]:
    """Calculates the distanced according to the algorithm in the constant variable algo.

    If the constant doBias is set to true, then the bias function is applied with the parameter
    completelyInsideOtherBias. If the constant readFromFile is set to true, then the algorithm won't execute, but
    rather load a cached representation from a json file, which will not work for all algorithms, but only those that
    were cached previously

    Args:
        strings: to calculate the distances for each combination
        completelyInsideOtherBias: parameter for the bias function, default = 0.7
        algo: to use for text distance comparison, default = "jaccard"
        readFromFile: if a cached text distance matrix should be read from a file, default = True
        writeToFile: if the calculated text distance matrix should be written to a file, default = True
        doBias: if the bias function should be applied, default = True

    Returns:
        list of tuples with the form (name1: String, name2: String, distanceValue: float)
    """

    def bias(s1, s2):
        if s1 in s2 or s2 in s1:
            return completelyInsideOtherBias
        else:
            return 0

    stringCombinations = set(map(frozenset, combinations(set(strings), 2)))

    if readFromFile:
        with open(PATH_PREFIX + "/" + algo + ".json", "r") as file:
            allDistances = json.loads(file.read())
    else:
        allDistances = [(s1, s2, s1 == s2 and -1 or td.jaccard(s1, s2)) for s1, s2 in stringCombinations]
        allDistances.sort(key=lambda x: x[2], reverse=True)
        if writeToFile:
            with open(PATH_PREFIX + "/" + algo + ".json", "w+") as file:
                file.write(json.dumps(allDistances))

    if doBias:
        for i in range(len(allDistances)):
            allDistances[i] = (allDistances[i][0], allDistances[i][1],
                               allDistances[i][2] + bias(allDistances[i][0], allDistances[i][1]))
    return allDistances


def convertToEqualityRings(distanceList: List[Tuple[str, str, float]]) -> List[List[str]]:
    """Converts a distance list of Tuples(str,str,float) into a list of sets with common elements merged.

    Example:
        convertToEqualityRings([("hello", "hellas", 0.8), ("hello", "bye", 0), ("test1", "test2", 0.8)])
        will return: [{"hello", "hellas", "bye"},{"test1", "test2"}]

    Args:
        distanceList: contains tuples of form: (name1: String, name2: String, distanceValue: float).
            The distanceValue is ignored and just the names are taken in to account, which are then used to merge all
            Tuples of form (name1: String, name2: String) into sets if they have any elements in common.

    Returns:
        a list of sets with common elements merged
    """
    sets = map(lambda x: set(x[0:2]), distanceList)
    return list(merge_common(sets))


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


class Statics:
    """
    Class that contains important static values.
    """
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


def preProcess(df: pd.DataFrame) -> pd.DataFrame:
    """Pre processes the given DataFrame by applying a lot of Regex replacements.

    Args:
        df: a pandas DataFrame to pre process

    Returns:
        a pre processed pandas DataFrame
    """
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


def compareToGold(df: pd.DataFrame, dupesets: List[Set[int]], dupeids: List[int]) -> Tuple[Set, Set, Set, Set, List]:
    """Compares the given DataFrame to the given Gold Standard and prints and returns the results

    Args:
        df: a pandas DataFrame to compare to the Gold Standard
        dupesets: the Gold Standard dupesets, see #loadGoldStandard()
        dupeids: the Gold Standard dupeids, see #loadGoldStandard()

    Returns:
        A Tuple (true_positive, false_negative, false_positive, true_negative, listofparams)
    """
    recognizedDuplicates = list(df[df.id.map(len) > 1].id)
    recognizedNonDuplicates = list(df[df.id.map(len) <= 1].id)
    true_positive = set()
    true_negative = set()
    false_negative = set()
    false_positive = set()
    for dupeset in dupesets:
        if dupeset in recognizedDuplicates:
            true_positive.add(frozenset(dupeset))
        else:
            false_negative.add(frozenset(dupeset))
    for recdup in recognizedDuplicates:
        if recdup in dupesets:
            true_positive.add(frozenset(recdup))
        else:
            false_positive.add(frozenset(recdup))
    for recnondup in recognizedNonDuplicates:
        if recnondup not in dupeids:
            true_negative.add(frozenset(recnondup))

    # times 2 because we work with sets of 2
    tp = len([e for s in true_positive for e in s])
    tn = len([e for s in true_negative for e in s])
    fn = len([e for s in false_negative for e in s])
    fp = len([e for s in false_positive for e in s])
    print("True positives: " + str(tp))
    print("True negatives: " + str(tn))
    print("False positives: " + str(fp))
    print("False negatives: " + str(fn))
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    fscore = (2 * precision * recall) / (precision + recall)
    print("Precision: " + str(precision))
    print("Recall: " + str(recall))
    print("Fscore: " + str(fscore))
    # print(ALGO,tp,tn,fp,fn,precision,recall,fscore, sep=",")
    listofparams = [ALGO, tp, tn, fp, fn, precision, recall, fscore]
    return true_positive, false_negative, false_positive, true_negative, listofparams


def __findClosestEqRingMatch(eqRing: List[List[str]], searchString: str) -> str:
    for i, ring in enumerate(eqRing):
        for e in ring:
            if e == searchString:
                return ring[0]
    return searchString


def dedupe(df: pd.DataFrame, eqRing: List[List[str]]) -> pd.DataFrame:
    """Deduplicates the given preprocessed DataFrame by using the eqRing.

    Args:
        df: a preprocessed pandas DataFrame
        eqRing: to use for grouping by

    Returns:
        a deduped pandas DataFrame
    """
    df["tdkey"] = df.cname.copy()
    df["tdkey"] = df["tdkey"].apply(lambda s: __findClosestEqRingMatch(eqRing, s))
    df = df.groupby(["phone", "tdkey"]).agg(set).reset_index()
    return df


eqRing = []


def clean(df: pd.DataFrame, completelyInsideOtherBias: float = 0.7, filterCutoff: float = 0.65) -> pd.DataFrame:
    """Main function to completely clean a restaurant dataset.

    Args:
        df: a pandas DataFrame
        completelyInsideOtherBias: float parameter for the bias function
        filterCutoff: float parameter specifying at which distance value to cut off the distance list

    Returns:
        a deduplicated pandas DataFrame
    """
    global eqRing
    df = preProcess(df)
    distances = calcDistances(df.cname.unique(), completelyInsideOtherBias)
    filteredDistances = list(filter(lambda x: x[2] >= filterCutoff, distances))
    eqRing = convertToEqualityRings(filteredDistances)
    return dedupe(df, eqRing)


def __firstOfSet(s: Any) -> Any:
    if isinstance(s, set):
        return s.pop()
    else:
        return s


def prepareUploadJsons(df: pd.DataFrame) -> pd.DataFrame:
    """Prepares and saves two json files that can be imported into mongodb.
        Look in ../data/work/deduped_raw.json and ../data/work/deduped_clean.json

    Args:
        df: a pandas DataFrame

    Returns:
        a pandas DataFrame
    """
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


PATH_PREFIX = "../data/work"

if __name__ == '__main__':
    dupesets, dupeids = loadGoldStandard()
    dataframe = pd.read_csv(PATH_PREFIX + '/restaurants.tsv', delimiter='\t')
    cleaned = clean(dataframe, 0.7, 0.65)
    compareToGold(cleaned, dupesets, dupeids)
    prepared = prepareUploadJsons(cleaned)

# CODE USED FOR GENERATING THE HEATMAP CHART
#    bias = 0.7
#    cutoff = 0.7
#    allparams = []
#    for bias in np.arange(0.0,1.1,0.1):
#        for cutoff in np.arange(0.0,1.1,0.1):
#            cleaned = clean(dataframe, bias, cutoff)
#            a,b,c,d,params = compareToGold(cleaned, dupesets, dupeids)
#            print(bias,cutoff,*params, sep=",")
#            allparams.append([bias,cutoff,*params])
#    print("##### ALL PARAMS:")
#    for p in allparams:
#        print(*p,sep=",")
