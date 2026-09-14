"""The four criteria, and whether their claimed difficulty order survives."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from claudish.corpus import cases
from claudish.tiers import (case_criteria, code_shaped, ladder, length_band,
                            measure_comment, score_run)
from claudish.io import digest, write_json
from claudish.filelevel import JUDGMENTS
from claudish import tiers

ROOT = Path(__file__).resolve().parents[1]

SOURCE = """// header
void helper() {}

void Widget::resize(unsigned Slots) {
  // <COMMENT_TO_WRITE>
  MaxSlots = Slots;
  rebuildIndexMap();
}
"""


def case():
    return {"id": "x", "path": "lib/Widget.cpp", "line": 5,
            "context": SOURCE, "source": SOURCE + "\nvoid Widget::drop() {}\n",
            "reference": "Growing past MaxSlots forces rebuildIndexMap, so callers "
                         "batch resizes rather than paying for each one separately "
                         "and the index stays valid for every live iterator here."}


def row(comment, deficits, upstream_deficits):
    grades = {"without_spec": deficits, "with_spec": deficits, "upstream": upstream_deficits}
    return {"id": "x", "comments": {"without_spec": comment, "with_spec": comment,
                                    "upstream": case()["reference"]},
            "judgments": [{"grades": grades}]}


def deficits(**overrides):
    base = dict.fromkeys(("claudishness", "words", "structure", "simplicity",
                          "meaning", "usefulness"), 0)
    return {**base, **overrides}


class Measures(unittest.TestCase):
    def test_only_unambiguous_code_names_count_as_code(self):
        self.assertTrue(all(map(code_shaped, ("MaxSlots", "rebuild_index", "LLVM_DEBUG", "BB"))))
        self.assertFalse(any(map(code_shaped, ("loop", "size", "I", "the"))))

    def test_restatement_counts_only_names_the_writer_could_see(self):
        visible = measure_comment("MaxSlots and rebuildIndexMap are updated", case())
        self.assertEqual(visible["restated_identifiers"], 2)
        self.assertEqual(visible["foreign_symbols"], 0)
        outside = measure_comment("This mirrors ScalarEvolution behaviour", case())
        self.assertEqual(outside["restated_identifiers"], 0)
        self.assertEqual(outside["foreign_symbol_names"], ["ScalarEvolution"])

    def test_length_bands_report_falling_outside_the_corpus_range(self):
        self.assertEqual((length_band(5), length_band(30), length_band(500)),
                         ("below", "short", "above"))

    def test_measures_run_on_every_real_corpus_case(self):
        corpus = cases(ROOT, "test", "corpus/scaled")
        for item in corpus:
            measured = measure_comment(item["reference"], item)
            self.assertEqual(measured["length_band"], item["length_band"])
            self.assertLessEqual(measured["restatement_fraction"], 1.0)


class SavedFileGrades(unittest.TestCase):
    def test_legacy_grades_are_ignored_and_v2_requires_matching_inputs(self):
        corpus = [case()]
        rows = [row(" ".join(["word"] * 40), deficits(), deficits())]
        grades = [{"path": case()["path"], "arm": arm, "optimal": {"passed": True}}
                  for arm in ("with_spec", "without_spec")]
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            write_json(output / "manifest.json", {"name": "fixture", "task_sha256": "task",
                                                   "spec_sha256": "spec"})
            write_json(output / "results.json", rows)
            write_json(output / "file-judgments.json", {"files": grades})
            result = score_run(output, lambda manifest: corpus)
            self.assertNotIn("optimal", result["ladder"]["with_spec"])
            saved = {"version": 2, "inputs": {"rows_sha256": digest(rows),
                                               "corpus_sha256": digest(corpus)}, "files": grades}
            write_json(output / JUDGMENTS, saved)
            result = score_run(output, lambda manifest: corpus)
            self.assertEqual(result["ladder"]["with_spec"]["optimal"]["passed"], 1)
            for key in ("rows_sha256", "corpus_sha256"):
                write_json(output / JUDGMENTS, {**saved, "inputs": {**saved["inputs"], key: "changed"}})
                with self.assertRaisesRegex(ValueError, "do not match"):
                    score_run(output, lambda manifest: corpus)


class Criteria(unittest.TestCase):
    def test_meaning_is_aggregated_once_for_both_precondition_fields(self):
        with patch("claudish.tiers._graded", wraps=tiers._graded) as graded:
            result = case_criteria(row("A local explanation.", deficits(meaning=2), deficits()),
                                   case(), "with_spec")
        meaning_calls = [call for call in graded.call_args_list if call.args[2] == ("meaning",)]
        self.assertEqual(len(meaning_calls), 1)
        self.assertEqual(result["precondition"], {"meaning": 2, "passed": False})

    def test_a_noticeable_style_deficit_fails_clean_even_when_upstream_is_worse(self):
        scored = case_criteria(row("Short note.", deficits(words=2), deficits(words=4)),
                               case(), "with_spec")
        self.assertFalse(scored["clean"]["passed"])
        # Still better than the upstream comment, which the verdict records separately.
        self.assertTrue(scored["clean"]["beats_upstream"])

    def test_effective_needs_both_the_right_length_and_the_right_subject(self):
        long_enough = " ".join(["word"] * 40)
        self.assertTrue(case_criteria(row(long_enough, deficits(), deficits()),
                                      case(), "with_spec")["effective"]["passed"])
        self.assertFalse(case_criteria(row("Too short.", deficits(), deficits()),
                                       case(), "with_spec")["effective"]["passed"])
        self.assertFalse(case_criteria(row(long_enough, deficits(usefulness=3), deficits()),
                                       case(), "with_spec")["effective"]["passed"])

    def test_naming_another_component_fails_invasive(self):
        reference_free = case_criteria(row(" ".join(["word"] * 40), deficits(), deficits()),
                                       case(), "with_spec")
        self.assertTrue(reference_free["invasive"]["passed"])
        coupled = case_criteria(row("ScalarEvolution decides " + " ".join(["word"] * 37),
                                    deficits(), deficits()), case(), "with_spec")
        self.assertFalse(coupled["invasive"]["passed"])

    def test_truthfulness_is_reported_beside_the_ladder_not_inside_it(self):
        scored = case_criteria(row(" ".join(["word"] * 40), deficits(meaning=3), deficits()),
                               case(), "with_spec")
        self.assertFalse(scored["precondition"]["passed"])
        self.assertTrue(scored["clean"]["passed"])


class Ladder(unittest.TestCase):
    def make(self, name, **passes):
        return {"id": name, **{key: {"passed": value} for key, value in passes.items()}}

    def test_each_rate_counts_only_the_cases_still_standing(self):
        summary = ladder([
            self.make("a", clean=True, effective=True, invasive=True),
            self.make("b", clean=True, effective=True, invasive=False),
            self.make("c", clean=True, effective=False, invasive=True),
            self.make("d", clean=False, effective=False, invasive=False)])
        self.assertEqual(summary["reached"]["clean"]["passed"], 3)
        self.assertEqual(summary["reached"]["effective"]["judged"], 3)
        self.assertEqual(summary["reached"]["invasive"]["judged"], 2)
        self.assertEqual(summary["first_failure"], {"clean": 1, "effective": 1,
                                                    "invasive": 1, "none": 1})

    def test_passing_a_harder_criterion_while_failing_an_easier_one_is_recorded(self):
        summary = ladder([self.make("c", clean=True, effective=False, invasive=True)])
        self.assertFalse(summary["order_holds"])
        violation = next(item for item in summary["order_violations"]
                         if item["harder"] == "invasive")
        self.assertEqual(violation["ids"], ["c"])


if __name__ == "__main__":
    unittest.main()
