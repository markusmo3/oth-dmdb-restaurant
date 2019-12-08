from unittest import TestCase

from src.clean import calcDistances, convertToEqualityRings


class Test(TestCase):
    def test_calc_distances(self):
        s1 = "Hallo Welt!"
        s2 = "Hello World!"
        s3 = "Hellas Amigos!"
        dists = calcDistances({s1, s2, s3})
        self.assertEqual(3, len(dists))
        onlyPairings = set(map(lambda x: frozenset(x[0:2]), dists))
        self.assertIn({s1, s2}, onlyPairings)
        self.assertIn({s2, s3}, onlyPairings)
        self.assertIn({s1, s3}, onlyPairings)
        # print(dists)
        # self.fail()

    def test_convert_to_equality_rings(self):
        inputList = [("s1", "s2", 1), ("s1", "s3", 1), ("s4", "s3", 1),
                ("a1", "a2", 1), ("c1", "a2", 1), ("a4", "a3", 1), ("b1", "b2", 1)]
        eqRing = convertToEqualityRings(inputList)
        self.assertIn(["s1", "s2", "s3", "s4"], eqRing)
        self.assertIn(["a1", "a2", "c1"], eqRing)
        self.assertIn(["a3", "a4"], eqRing)
        self.assertIn(["b1", "b2"], eqRing)
        print(eqRing)
        # self.fail()
