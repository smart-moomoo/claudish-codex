"""Invariants for the 500-comment, file-disjoint LLVM corpus."""

from collections import Counter
from pathlib import Path
import unittest

from claudish.corpus import cases
from claudish.metrics import measure

ROOT = Path(__file__).resolve().parents[1]
EARLIER = ("corpus", "corpus/long-blocks", "corpus/scaled")
BANDS = {"short": (20, 49), "medium": (50, 99), "long": (100, 300)}


class ScaledFiveHundredContracts(unittest.TestCase):
    def setUp(self):
        self.rows = cases(ROOT, corpus_dir="corpus/scaled-500")

    def test_counts_and_length_strata(self):
        self.assertEqual(len(self.rows), 500)
        self.assertEqual(Counter(row["split"] for row in self.rows),
                         {"train": 250, "validation": 130, "test": 120})
        self.assertEqual(Counter((row["split"], row["length_band"]) for row in self.rows), {
            ("train", "short"): 84, ("train", "medium"): 83, ("train", "long"): 83,
            ("validation", "short"): 44, ("validation", "medium"): 43,
            ("validation", "long"): 43,
            ("test", "short"): 40, ("test", "medium"): 40, ("test", "long"): 40,
        })

    def test_every_reference_sits_in_its_declared_band(self):
        for row in self.rows:
            low, high = BANDS[row["length_band"]]
            self.assertLessEqual(low, measure(row["reference"])["word_count"])
            self.assertLessEqual(measure(row["reference"])["word_count"], high)

    def test_files_are_capped_split_pure_and_new(self):
        per_file = Counter(row["path"] for row in self.rows)
        self.assertLessEqual(max(per_file.values()), 6)
        split_of = {}
        for row in self.rows:
            self.assertEqual(split_of.setdefault(row["path"], row["split"]), row["split"])
        earlier = {row["path"] for corpus_dir in EARLIER
                   for row in cases(ROOT, corpus_dir=corpus_dir)}
        self.assertTrue(earlier.isdisjoint(per_file))

    def test_each_context_masks_exactly_one_location(self):
        for row in self.rows:
            self.assertEqual(row["context"].count("<COMMENT_TO_WRITE>"), 1)


if __name__ == "__main__":
    unittest.main()
