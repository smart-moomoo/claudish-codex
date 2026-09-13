"""Focused invariants for the scaled, file-disjoint LLVM corpus."""

from collections import Counter
from pathlib import Path
import unittest

from claudish.corpus import cases


ROOT = Path(__file__).resolve().parents[1]


class ScaledCorpusContracts(unittest.TestCase):
    def test_counts_strata_caps_and_retired_files(self):
        rows = cases(ROOT, corpus_dir="corpus/scaled")
        self.assertEqual(Counter(row["split"] for row in rows),
                         {"train": 75, "validation": 40, "test": 35})
        self.assertEqual(Counter((row["split"], row["length_band"]) for row in rows), {
            ("train", "short"): 25, ("train", "medium"): 25, ("train", "long"): 25,
            ("validation", "short"): 14, ("validation", "medium"): 13,
            ("validation", "long"): 13,
            ("test", "short"): 12, ("test", "medium"): 12, ("test", "long"): 11,
        })
        self.assertLessEqual(max(Counter(row["path"] for row in rows).values()), 6)
        earlier = {row["path"] for corpus_dir in ("corpus", "corpus/long-blocks")
                   for row in cases(ROOT, corpus_dir=corpus_dir)}
        self.assertTrue(earlier.isdisjoint(row["path"] for row in rows))
        self.assertTrue(all(row["context"].count("<COMMENT_TO_WRITE>") == 1 for row in rows))


if __name__ == "__main__":
    unittest.main()
