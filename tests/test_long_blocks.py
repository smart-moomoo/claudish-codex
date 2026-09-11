"""Contracts specific to the long-block sampling stratum."""

from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from claudish.corpus import cases
from claudish.io import read_json
from claudish.metrics import measure

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "corpus/long-blocks"


class LongBlockContracts(unittest.TestCase):
    def test_frozen_stratum_and_file_splits(self):
        rows = cases(ROOT, corpus_dir="corpus/long-blocks")
        self.assertEqual(len(rows), 12)
        files = {}
        for row in rows:
            self.assertLessEqual(100, measure(row["reference"])["word_count"])
            self.assertLessEqual(measure(row["reference"])["word_count"], 300)
            self.assertEqual(row["context"].count("<COMMENT_TO_WRITE>"), 1)
            self.assertEqual(files.setdefault(row["path"], row["split"]), row["split"])
        self.assertEqual([sum(c["split"] == s for c in rows)
                          for s in ("train", "validation", "test")], [4, 4, 4])

    def test_length_guard_and_extra_context_leakage(self):
        for change, message in (({"min_reference_words": 300}, "length outside"),
                                ({"extra_context_ranges": [[2631, 2632]]}, "includes target")):
            frozen = deepcopy(read_json(DATA / "cases.json"))
            frozen[0].update(change)
            selection = [{k: v for k, v in c.items() if k != "reference_sha256"} for c in frozen]

            def altered(path):
                path = Path(path)
                if path == DATA / "cases.json":
                    return frozen
                if path == DATA / "selection.json":
                    return selection
                return read_json(path)

            with patch("claudish.corpus.read_json", side_effect=altered):
                with self.assertRaisesRegex(ValueError, message):
                    cases(ROOT, corpus_dir=DATA)

    def test_paragraph_metrics_ignore_physical_wrapping(self):
        wrapped = "Keep this value\nfor the caller.\n\nFree it after use."
        flat = "Keep this value for the caller.\n\nFree it after use."
        self.assertEqual(measure(wrapped), measure(flat))
        self.assertEqual(measure(flat)["paragraph_count"], 2)
        self.assertEqual(measure("")["paragraph_count"], 0)


if __name__ == "__main__":
    unittest.main()
