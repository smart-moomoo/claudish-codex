"""Positions where a comment may or may not belong, and telling them apart."""

from pathlib import Path
import unittest

from claudish.io import read_json, safe_path
from claudish.placement import MARKER, anchors, cases, outcome, summarize, take

ROOT = Path(__file__).resolve().parents[1]
CORPUS = "corpus/scaled-500"


class Anchors(unittest.TestCase):
    def test_a_position_under_a_nearby_comment_is_not_treated_as_uncommented(self):
        source = "int x;\n" * 25 + "\n// explained above\nnamespace {\n\nclass Thing {\n"
        self.assertEqual(anchors(source), [])

    def test_code_after_a_blank_line_with_nothing_commented_nearby_qualifies(self):
        source = "int x;\n" * 25 + "\n  Value = compute();\n" + "int y;\n"
        self.assertEqual(anchors(source), [27])

    def test_the_last_line_of_a_file_can_still_be_an_anchor(self):
        source = "int x;\n" * 25 + "\n  Value = compute();"
        self.assertEqual(anchors(source), [27])

    def test_closing_braces_and_directives_are_never_anchors(self):
        source = "int x;\n" * 25 + "\n}\n\n#include <x>\n"
        self.assertEqual(anchors(source), [])


class Corpus(unittest.TestCase):
    def setUp(self):
        self.rows = cases(ROOT, "train", CORPUS)

    def test_the_two_kinds_are_balanced_and_stay_inside_one_split(self):
        kinds = [row["kind"] for row in self.rows]
        self.assertEqual(kinds.count("commented"), kinds.count("uncommented"))
        lock = read_json(ROOT / CORPUS / "sources.lock.json")
        split_of = {record["path"]: record["split"] for record in lock["files"]}
        for row in self.rows:
            self.assertEqual(split_of[row["path"]], "train")

    def test_both_kinds_look_the_same_and_never_show_the_answer(self):
        for row in self.rows:
            self.assertEqual(row["context"].count(MARKER), 1)
            self.assertIs(row["expected_needed"], row["kind"] == "commented")
            if row["reference"]:
                normalized = " ".join(row["context"].split())
                for line in row["reference"].splitlines():
                    if len(line.strip()) > 30:
                        self.assertNotIn(" ".join(line.split()), normalized)

    def test_an_uncommented_position_really_has_no_comment_there(self):
        for row in self.rows:
            if row["kind"] != "uncommented":
                continue
            source = safe_path(ROOT / CORPUS / "upstream", row["path"]).read_text()
            above = source.splitlines()[row["line"] - 3:row["line"] - 1]
            self.assertFalse(any(line.strip().startswith(("//", "/*", "*")) for line in above))


class Subsets(unittest.TestCase):
    def setUp(self):
        self.rows = cases(ROOT, "train", CORPUS)

    def test_a_partial_run_keeps_both_kinds_evenly(self):
        chosen = take(self.rows, 10)
        kinds = [case["kind"] for case in chosen]
        self.assertEqual((kinds.count("commented"), kinds.count("uncommented")), (5, 5))

    def test_a_smaller_run_asks_a_subset_of_the_larger_one(self):
        self.assertTrue({case["id"] for case in take(self.rows, 10)}
                        .issubset({case["id"] for case in take(self.rows, 20)}))
        self.assertEqual(len(take(self.rows, None)), len(self.rows))

    def test_an_odd_or_oversized_request_is_refused(self):
        with self.assertRaisesRegex(ValueError, "even, positive"):
            take(self.rows, 7)
        with self.assertRaisesRegex(ValueError, "available"):
            take(self.rows, len(self.rows) + 2)


class Decisions(unittest.TestCase):
    def case(self, kind):
        return {"kind": kind, "expected_needed": kind == "commented"}

    def test_an_answer_that_contradicts_itself_is_excluded(self):
        for answer in ({"needed": False, "reason": "no", "comment": "but here it is"},
                       {"needed": True, "reason": "yes", "comment": "   "},
                       {"needed": "yes", "reason": "r", "comment": "c"}):
            decision, invalid = outcome(answer, self.case("commented"))
            self.assertIsNone(decision)
            self.assertTrue(invalid)

    def test_agreement_is_measured_against_what_llvm_did(self):
        decision, invalid = outcome({"needed": False, "reason": "obvious", "comment": ""},
                                    self.case("uncommented"))
        self.assertIsNone(invalid)
        self.assertTrue(decision["agrees"])
        self.assertEqual(decision["words"], 0)

    def test_always_saying_yes_shows_up_as_no_discrimination(self):
        decisions = [{"expected": True, "needed": True, "agrees": True},
                     {"expected": False, "needed": True, "agrees": False}]
        summary = summarize(decisions)
        self.assertEqual(summary["discrimination"], 0.0)
        self.assertTrue(summary["always_says_yes"])
        self.assertEqual(summary["agreement"], 0.5)


if __name__ == "__main__":
    unittest.main()
