#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated tests for the parsing module.
"""

import logging
import unittest
import numpy as np

from gensim.parsing.tfidf import *
from gensim.parsing.preprocessing import *


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.WARNING)


# several documents
doc1 = """C'est un trou de verdure où chante une rivière,
Accrochant follement aux herbes des haillons
D'argent ; où le soleil, de la montagne fière,
Luit : c'est un petit val qui mousse de rayons."""

doc2 = """Un soldat jeune, bouche ouverte, tête nue,
Et la nuque baignant dans le frais cresson bleu,
Dort ; il est étendu dans l'herbe, sous la nue,
Pâle dans son lit vert où la lumière pleut."""

doc3 = """Les pieds dans les glaïeuls, il dort. Souriant comme
Sourirait un enfant malade, il fait un somme :
Nature, berce-le chaudement : il a froid."""

doc4 = """Les parfums ne font pas frissonner sa narine ;
Il dort dans le soleil, la main sur sa poitrine,
Tranquille. Il a deux trous rouges au côté droit."""

doc5 = """While it is quite useful to be able to search a
large collection of documents almost instantly for a joint
occurrence of a collection of exact words,
for many searching purposes, a little fuzziness would help. """


dataset = map(lambda x: strip_punctuation2(x.lower()),
        [doc1, doc2, doc3, doc4])
# doc1 and doc2 have class 0, doc3 and doc4 avec class 1
classes = np.array([[1, 0], [1, 0], [0, 1], [0, 1]])


class TestTfidf(unittest.TestCase):

    def testTokenize(self):
        self.assertEquals(tokenize("salut les amis"),
                          ["salut", "les", "amis"])

        self.assertEquals(tokenize("salut  les   amis "),
                          ["salut", "les", "amis"])

        self.assertEquals(tokenize("Salut  LES   amis !"),
                          ["Salut", "LES", "amis", "!"])

    def testTermCounts(self):
        term_counts, vocab = tc(dataset)
        self.assertEquals(len(term_counts), len(dataset))
        for i in range(len(dataset)):
            # len of the documents should be equal to the sum of word counts
            self.assertEquals(len(tokenize(dataset[i])),
                              sum(term_counts[i].values()))

        self.assertEquals(term_counts[0]["la"], 1)
        self.assertEquals(term_counts[1]["la"], 3)
        self.assertRaises(KeyError, term_counts[2].__getitem__, "la")
        self.assertEquals(term_counts[3]["la"], 1)

    def testTermFrequencies(self):
        term_counts, vocab = tc(dataset)
        term_frequencies = tf_from_tc(term_counts)
        for doc in term_frequencies:
            self.assertAlmostEquals(sum(doc.values()), 1.0)

        self.assertTrue(term_frequencies[0]["la"] > 0)
        self.assertTrue(term_frequencies[1]["la"] > 0)
        self.assertRaises(KeyError, term_frequencies[2].__getitem__, "la")
        self.assertTrue(term_frequencies[3]["la"] > 0)

    def testInvertDocumentCounts(self):
        term_counts, vocab = tc(dataset)
        inv_doc_counts = idc_from_tc(term_counts)
        self.assertEquals(len(vocab), len(inv_doc_counts))
        self.assertEquals(inv_doc_counts["la"], 3)

    def testInvertDocumentFrequencies(self):
        term_counts, vocab = tc(dataset)
        inv_doc_freq = idf_from_tc(term_counts)
        self.assertEquals(len(vocab), len(inv_doc_freq))
        self.assertTrue(inv_doc_freq["la"] > 0)
        to_vector(inv_doc_freq, vocab)

    def testTFIDFDict(self):
        td, v = tfidf(dataset).as_dict()
        self.assertTrue(td[0]["la"] > 0)
        self.assertTrue(td[1]["la"] > 0)
        self.assertRaises(KeyError, td[2].__getitem__, "la")
        self.assertTrue(td[3]["la"] > 0)

    def testTFIDFArray(self):
        td, v = tfidf(dataset).as_array()


class TestPreprocessing(unittest.TestCase):

    def testStripNumeric(self):
        self.assertEquals(strip_numeric("salut les amis du 59"),
                          "salut les amis du ")

    def testStripShort(self):
        self.assertEquals(strip_short("salut les amis du 59", 3),
                          "salut les amis")

    def testStripTags(self):
        self.assertEquals(strip_tags("<i>Hello</i> <b>World</b>!"),
                          "Hello World!")

    def testStripMultipleWhitespaces(self):
        self.assertEquals(strip_multiple_whitespaces("salut  les\r\nloulous!"),
                          "salut les loulous!")

    def testStripNonAlphanum(self):
        self.assertEquals(strip_non_alphanum("toto nf-kappa titi"),
                          "toto nf kappa titi")

    def testSplitAlphanum(self):
        self.assertEquals(split_alphanum("toto diet1 titi"),
                          "toto diet 1 titi")
        self.assertEquals(split_alphanum("toto 1diet titi"),
                          "toto 1 diet titi")

    def testStripStopwords(self):
        self.assertEquals(remove_stopwords("the world is square"),
                          "world square")

    def testStemText(self):
        target = "while it is quit us to be abl to search a larg " + \
                "collect of document almost instantli for a joint occurr " + \
                "of a collect of exact words, for mani search purposes, " + \
                "a littl fuzzi would help."
        self.assertEquals(stem_text(doc5), target)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    unittest.main()
