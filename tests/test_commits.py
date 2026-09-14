"""Real commits as the unit: what an answer touches, and whether it applies."""

import unittest
from pathlib import Path
import tempfile

from claudish.commits import (apply_edits, compare, eligible, message_of,
                              parse_patch, reference_change, shape, _write_results)
from claudish.io import read_json

PATCH = """From 0badc0de Mon Sep 17 00:00:00 2001
From: Someone <someone@example.com>
Date: Sun, 22 Mar 2020 22:18:40 +0100
Subject: [PATCH] Clamp the slot count before rebuilding the index

Callers passed unbounded counts and the index map grew without limit.
Reviewers: nobody
Differential Revision: https://reviews.llvm.org/D00000
---
 llvm/lib/Widget/Widget.cpp | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)

diff --git a/llvm/lib/Widget/Widget.cpp b/llvm/lib/Widget/Widget.cpp
index 1111111..2222222 100644
--- a/llvm/lib/Widget/Widget.cpp
+++ b/llvm/lib/Widget/Widget.cpp
@@ -2,4 +2,5 @@ void Widget::resize(unsigned Slots) {
-  unsigned Old = MaxSlots;
+  const unsigned Old = MaxSlots;
-  MaxSlots = Slots;
+  MaxSlots = std::min(Slots, SlotLimit);
+  assert(MaxSlots >= Old);
   rebuildIndexMap();
 }
"""

SOURCE = """void Widget::resize(unsigned Slots) {
  unsigned Old = MaxSlots;
  MaxSlots = Slots;
  rebuildIndexMap();
}
"""
SOURCES = {"llvm/lib/Widget/Widget.cpp": SOURCE}


class Patches(unittest.TestCase):
    def test_the_message_drops_the_patch_prefix_and_review_trailers(self):
        subject, body = message_of(PATCH)
        self.assertEqual(subject, "Clamp the slot count before rebuilding the index")
        self.assertEqual(body, "Callers passed unbounded counts and the index map grew without limit.")

    def test_a_patch_reports_the_lines_it_touches_before_the_change(self):
        section, = parse_patch(PATCH)
        self.assertEqual(section["path"], "llvm/lib/Widget/Widget.cpp")
        self.assertEqual(section["touched"], {2, 3})
        self.assertEqual(len(section["added"]), 3)

    def test_eligibility_refuses_large_reverts_and_non_library_files(self):
        subject, body = message_of(PATCH)
        sections = parse_patch(PATCH)
        self.assertIsNone(eligible(subject, body, sections))
        self.assertIn("revert", eligible("Revert this", body, sections))
        outside = [{**sections[0], "path": "clang/lib/Sema/Sema.cpp"}]
        self.assertIn("outside", eligible(subject, body, outside))
        big = [{**sections[0], "added": ["x"] * 100, "removed": []}]
        self.assertEqual(eligible(subject, body, big), "too large")
        self.assertEqual(eligible("Fix", "it", sections),
                         "message is too short to act on")


class Answers(unittest.TestCase):
    def test_anchor_width_trailing_newline_and_sequential_offsets_do_not_change_shape(self):
        source = "int a = 0;\nint b = 0;\nint c = 0;\n"
        after = source.replace("b = 0", "b = 1")
        def apply(edits):
            result, invalid = apply_edits({"edits": [{"path": "a.cpp", "old_text": old,
                                                       "new_text": new} for old, new in edits],
                                            "explanation": "Fixture."}, {"a.cpp": source})
            self.assertIsNone(invalid)
            return result["shape"]
        narrow = apply([("b = 0", "b = 1")])
        self.assertEqual(narrow["touched_lines"], {"a.cpp": [2]})
        self.assertEqual(narrow, apply([(source, after)]))
        self.assertEqual(narrow, apply([("int b = 0;\n", "int b = 1;\n")]))
        self.assertEqual(narrow, apply([("int a", "// temporary\nint a"),
                                        ("b = 0", "b = 1"), ("// temporary\n", "")]))

    def test_patch_and_generated_answer_use_identical_final_diff(self):
        import difflib
        source = "alpha\nbeta\ngamma\n"
        for after in ("new\n" + source, source + "new\n", "alpha\ngamma\n",
                      source.rstrip("\n")):
            with self.subTest(after=after):
                lines = list(difflib.unified_diff(source.splitlines(keepends=True),
                                                after.splitlines(keepends=True),
                                                fromfile="a/a.cpp", tofile="b/a.cpp"))
                patch = "diff --git a/a.cpp b/a.cpp\n" + "".join(
                    line if line.endswith("\n") else line + "\n\\ No newline at end of file\n"
                    for line in lines)
                applied, _ = apply_edits({"edits": [{"path": "a.cpp", "old_text": source,
                                                      "new_text": after}],
                                           "explanation": "Fixture."}, {"a.cpp": source})
                self.assertEqual(applied["shape"], reference_change(patch, {"a.cpp": source}))

    def test_edits_that_cancel_each_other_are_not_a_change(self):
        applied, invalid = apply_edits({"edits": [
            {"path": "a.cpp", "old_text": "one", "new_text": "two"},
            {"path": "a.cpp", "old_text": "two", "new_text": "one"}],
            "explanation": "Fixture."}, {"a.cpp": "one"})
        self.assertIsNone(applied)
        self.assertIn("no net change", invalid)

    def edit(self, **overrides):
        return {"edits": [{"path": "llvm/lib/Widget/Widget.cpp",
                           "old_text": "  MaxSlots = Slots;",
                           "new_text": "  MaxSlots = std::min(Slots, SlotLimit);", **overrides}],
                "explanation": "Clamped the count."}

    def test_an_edit_that_applies_reports_the_lines_it_replaced(self):
        applied, invalid = apply_edits(self.edit(), SOURCES)
        self.assertIsNone(invalid)
        self.assertEqual(applied["shape"]["touched_lines"], {"llvm/lib/Widget/Widget.cpp": [3]})
        self.assertEqual(applied["shape"]["new_symbols"], ["SlotLimit"])
        self.assertIn("std::min", applied["after"]["llvm/lib/Widget/Widget.cpp"])

    def test_text_that_is_missing_or_repeated_does_not_apply(self):
        for overrides, message in (({"old_text": "not present"}, "exactly once"),
                                   ({"old_text": "\n"}, "exactly once"),
                                   ({"path": "other.cpp"}, "not supplied"),
                                   ({"new_text": "  MaxSlots = Slots;"}, "changes nothing")):
            applied, invalid = apply_edits(self.edit(**overrides), SOURCES)
            self.assertIsNone(applied)
            self.assertIn(message, invalid)

    def test_an_answer_with_no_edits_does_not_apply(self):
        applied, invalid = apply_edits({"edits": [], "explanation": "nothing to do"}, SOURCES)
        self.assertIsNone(applied)
        self.assertIn("no edits", invalid)


class ResultArtifacts(unittest.TestCase):
    def test_shared_writer_preserves_case_counts_arms_and_row_order(self):
        manifest = {"name": "fixture", "split": "train", "model": "fixture", "effort": "medium",
                    "case_ids": ["a", "b"], "arms": ["without_spec", "with_spec"],
                    "overlap_threshold": 0.5}
        rows = [{"id": case, "arm": arm, "applied": False, "invalid": "Synthetic invalid answer."}
                for case in ("b", "a") for arm in manifest["arms"]]
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            summary = _write_results(output, manifest, rows)
            self.assertEqual(summary["cases"], 2)
            self.assertEqual(list(summary["arms"]), manifest["arms"])
            self.assertEqual(summary["arms"]["without_spec"]["cases"], 2)
            self.assertEqual(read_json(output / "summary.json"), summary)
            self.assertEqual(read_json(output / "results.json"), sorted(rows, key=lambda r: (r["id"], r["arm"])))
            self.assertIn("did not apply", (output / "report.md").read_text())


class Comparison(unittest.TestCase):
    def setUp(self):
        self.reference = reference_change(PATCH, SOURCES)

    def test_the_real_commit_reduces_to_the_same_measures_as_an_answer(self):
        self.assertEqual(self.reference["touched_lines"], {"llvm/lib/Widget/Widget.cpp": [2, 3]})
        self.assertEqual(self.reference["headers_touched"], [])
        self.assertIn("SlotLimit", self.reference["new_symbols"])

    def test_changing_the_same_line_passes_both_shape_criteria(self):
        applied, _ = apply_edits({"edits": [{"path": "llvm/lib/Widget/Widget.cpp",
                                             "old_text": "  MaxSlots = Slots;",
                                             "new_text": "  MaxSlots = std::min(Slots, SlotLimit);"}],
                                  "explanation": "x"}, SOURCES)
        result = compare(applied["shape"], self.reference)
        self.assertTrue(result["floor_passed"])
        self.assertTrue(result["invasive"]["passed"])
        self.assertTrue(result["optimal"]["passed"])

    def test_changing_a_different_place_fails_before_any_shape_measure(self):
        applied, _ = apply_edits({"edits": [{"path": "llvm/lib/Widget/Widget.cpp",
                                             "old_text": "  rebuildIndexMap();",
                                             "new_text": "  rebuildIndexMap(true);"}],
                                  "explanation": "x"}, SOURCES)
        result = compare(applied["shape"], self.reference)
        self.assertEqual(result["region_overlap"], 0.0)
        self.assertFalse(result["floor_passed"])
        self.assertFalse(result["optimal"]["passed"])

    def test_touching_a_header_the_real_change_left_alone_fails_invasive(self):
        candidate = shape({"llvm/lib/Widget/Widget.cpp": {3}, "llvm/include/llvm/Widget.h": {9}},
                          [], {**SOURCES, "llvm/include/llvm/Widget.h": "class Widget;\n"})
        result = compare(candidate, self.reference)
        self.assertEqual(result["invasive"]["headers_touched_beyond_reference"],
                         ["llvm/include/llvm/Widget.h"])
        self.assertFalse(result["invasive"]["passed"])


if __name__ == "__main__":
    unittest.main()
