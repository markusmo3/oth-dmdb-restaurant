import unittest
from io import BytesIO

import textdistance as td
import tokenize as to

def tokenize(s: str):
    return s.split()

class TestTextDistance(unittest.TestCase):
    def test_jaccard(self):
        print(td.jaccard("Hello", "Hello"))
        print(td.jaccard("Hello", "Hella"))
        print(td.jaccard("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaHello", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaHella"))
        print(td.jaccard("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaHello", "Hellaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"))
        print(td.jaccard("Hello World Test", "World Test Hello"))
        print(td.jaccard("Hello World Test", "Test World Hello"))
        print(td.jaccard("Hello World Test", "deeHllloorsTtW  "))

        print("Result of tokenizing a sentence:", tokenize("Hello World Test"))
        print(td.jaccard(tokenize("Hello World Test"), tokenize("deeHllloorsTtW  ")))
        print(td.jaccard(tokenize("Hello World Test"), tokenize("World Test Hello")))
        print(td.jaccard(tokenize("Hello World Test"), tokenize("Test World Hello")))



if __name__ == '__main__':
    unittest.main()
