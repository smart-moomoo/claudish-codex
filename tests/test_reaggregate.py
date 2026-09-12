"""Offline rebuilding of a run's summary, including runs with excluded pairs."""

import json
from pathlib import Path
import tempfile
import unittest

from claudish.experiment import reaggregate, _build_row
from claudish.io import digest, write_json
from claudish.judge import DIMENSIONS

LABELS = {"C1": "without_spec", "C2": "with_spec", "C3": "upstream"}
RUBRIC = "Grade the candidates.\n"
SPEC = "Write plain comments.\n"


def grade(label, score, evidence=()):
    return {"label": label, **dict.fromkeys(DIMENSIONS, score), "evidence": list(evidence),
            "explanation": "Scored.", "missing_facts": [], "unsupported_claims": []}


def judgment(score):
    return {"grades": {arm: grade(label, score) for label, arm in LABELS.items()},
            "blind_mapping": LABELS, "rubric_sha256": digest(RUBRIC)}


def case(index):
    return {"id": f"case-{index}", "path": "llvm/lib/X.cpp", "line": 10 + index,
            "source_url": "https://example.invalid/X.cpp", "reference": "Upstream comment text.",
            "length_band": "short", "functional_class": "mechanism"}


def comments(index):
    return {"without_spec": f"Baseline comment {index}.",
            "with_spec": f"Treatment comment {index}.",
            "upstream": "Upstream comment text."}


def build_run(directory, rows, excluded_pairs=()):
    manifest = {"name": "fixture", "status": "completed", "split": "validation", "repeats": 1,
                "judges_per_pair": 2, "model": "gpt-5.6-sol", "effort": "medium", "seed": 42,
                "spec_sha256": digest(SPEC), "rubric_sha256": digest(RUBRIC),
                "case_ids": [row["id"] for row in rows] + [item["id"] for item in excluded_pairs]}
    (directory / "rubric.md").write_text(RUBRIC)
    (directory / "spec.md").write_text(SPEC)
    write_json(directory / "manifest.json", manifest)
    write_json(directory / "results.json", rows)
    write_json(directory / "summary.json", {
        "requested_pairs": len(rows) + len(excluded_pairs),
        "excluded_generation_pairs": list(excluded_pairs)})


class Reaggregation(unittest.TestCase):
    def test_excluded_pair_does_not_block_rebuilding(self):
        rows = [_build_row(case(index), 0, comments(index), [judgment(1), judgment(2)])
                for index in range(3)]
        excluded = [{"id": "case-9", "repeat": 0,
                     "arms": {"with_spec": "Generator returned an unsafe comment delimiter"}}]
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            build_run(directory, rows, excluded)
            summary = reaggregate(directory)
        self.assertEqual(summary["pairs"], 3)
        self.assertEqual(summary["requested_pairs"], 4)
        self.assertEqual(summary["excluded_generation_pairs"], excluded)
        self.assertEqual(summary["valid_judgments"], 6)
        self.assertEqual(summary["recovered_judgments"], 0)

    def test_preserved_judgment_is_recovered_without_a_model_call(self):
        row = _build_row(case(0), 0, comments(0), [judgment(1)])
        raw = {"grades": [grade(label, 3) for label in LABELS]}
        row["invalid_judgments"] = [{"invalid": "Judge evidence must occur in the comment",
                                     "raw_answer": raw, "blind_mapping": LABELS,
                                     "rubric_sha256": digest(RUBRIC)}]
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            build_run(directory, [row])
            summary = reaggregate(directory)
            stored = json.loads((directory / "results.json").read_text())
        self.assertEqual(summary["recovered_judgments"], 1)
        self.assertEqual(summary["valid_judgments"], 2)
        self.assertEqual(summary["invalid_judgments"], 0)
        # Both judgments now contribute; the mean of 1 and 3 is reported.
        self.assertEqual(summary["grades"]["with_spec"]["meaning"], 2)
        self.assertNotIn("judge", stored[0])

    def test_an_unrecoverable_judgment_stays_preserved_and_excluded(self):
        row = _build_row(case(0), 0, comments(0), [judgment(1)])
        raw = {"grades": [grade(label, 3, evidence=["never written"]) for label in LABELS]}
        row["invalid_judgments"] = [{"invalid": "Judge evidence must occur in the comment",
                                     "raw_answer": raw, "blind_mapping": LABELS,
                                     "rubric_sha256": digest(RUBRIC)}]
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            build_run(directory, [row])
            summary = reaggregate(directory)
        self.assertEqual(summary["recovered_judgments"], 0)
        self.assertEqual(summary["invalid_judgments"], 1)
        self.assertEqual(summary["grades"]["with_spec"]["meaning"], 1)

    def test_a_changed_rubric_is_rejected(self):
        rows = [_build_row(case(0), 0, comments(0), [judgment(1)])]
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            build_run(directory, rows)
            (directory / "rubric.md").write_text("Different rubric.\n")
            with self.assertRaisesRegex(ValueError, "rubric checksum"):
                reaggregate(directory)


if __name__ == "__main__":
    unittest.main()
