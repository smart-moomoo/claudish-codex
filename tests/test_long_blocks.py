"""Contracts specific to the long-block sampling stratum."""

from pathlib import Path
import shutil
import tempfile
import unittest

from claudish.corpus import cases
from claudish.io import read_json, write_json
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
        # A real copy of the corpus on disk, so the loader's own file reads are tested.
        for change, message in (({"min_reference_words": 300}, "length outside"),
                                ({"extra_context_ranges": [[2631, 2632]]}, "includes target")):
            with tempfile.TemporaryDirectory() as directory:
                corpus_dir = Path(directory) / "long-blocks"
                shutil.copytree(DATA, corpus_dir)
                frozen = read_json(corpus_dir / "cases.json")
                frozen[0].update(change)
                write_json(corpus_dir / "cases.json", frozen)
                write_json(corpus_dir / "selection.json",
                           [{k: v for k, v in case.items() if k != "reference_sha256"}
                            for case in frozen])
                with self.assertRaisesRegex(ValueError, message):
                    cases(ROOT, corpus_dir=corpus_dir)

    def test_paragraph_metrics_ignore_physical_wrapping(self):
        wrapped = "Keep this value\nfor the caller.\n\nFree it after use."
        flat = "Keep this value for the caller.\n\nFree it after use."
        self.assertEqual(measure(wrapped), measure(flat))
        self.assertEqual(measure(flat)["paragraph_count"], 2)
        self.assertEqual(measure("")["paragraph_count"], 0)


if __name__ == "__main__":
    unittest.main()
