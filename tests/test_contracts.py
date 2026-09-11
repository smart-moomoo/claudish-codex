"""Focused contracts for experiment validity and safe comment extraction."""

import difflib
from pathlib import Path
import tempfile
import unittest

from claudish.cpp import scan, render_comment, assert_code_preserved
from claudish.diff import extract
from claudish.judge import DIMENSIONS, validate
from claudish.metrics import distance, summarize


class CommentContracts(unittest.TestCase):
    def test_literals_are_not_comments_and_multiline_comments_stay_whole(self):
        source = 'auto a = R"tag(// fake /* fake */)tag";\nconst char *b = "https://x/*";\n// first\n// second\nint x; /* actual\n * block */\n'
        comments, _ = scan(source)
        self.assertEqual([c.text for c in comments], ["first\nsecond", "actual\nblock"])
        self.assertEqual((comments[0].line, comments[0].end_line), (3, 4))

    def test_partial_comment_change_returns_entire_comment(self):
        before = '// first line\n// old condition\nint x = 1;\n'
        after = '// first line\n// new condition\nint x = 1;\n'
        with tempfile.TemporaryDirectory() as root:
            Path(root, "x.cpp").write_text(before)
            patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/x.cpp', tofile='b/x.cpp', n=0))
            result = extract(patch, root)
        self.assertEqual(len(result["comments"]), 1)
        self.assertEqual(result["comments"][0]["comment"], "first line\nnew condition")
        self.assertEqual(result["comments"][0]["line"], 1)

    def test_multiple_hunks_and_files_use_correct_new_locations(self):
        before = "int x;\n// before\nint y;\nint z;\n// last\nint w;\n"
        after = "int x;\n// after\n// explanation\nint y;\nint z;\n// end\nint w;\n"
        with tempfile.TemporaryDirectory() as root:
            patch = ""
            for name in ("x.cpp", "y.cpp"):
                Path(root, name).write_text(before)
                patch += ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/'+name, tofile='b/'+name, n=0))
            result = extract(patch, root)
        self.assertEqual([x["line"] for x in result["comments"]], [2, 6, 2, 6])

    def test_code_changes_and_incorrect_base_are_rejected(self):
        before = "int x = 1; // old\n"
        with tempfile.TemporaryDirectory() as root:
            Path(root, "x.cpp").write_text(before)
            patch = ''.join(difflib.unified_diff(before.splitlines(True), ["int x = 2; // new\n"], fromfile='a/x.cpp', tofile='b/x.cpp'))
            with self.assertRaisesRegex(ValueError, "Executable tokens"):
                extract(patch, root)
            with self.assertRaisesRegex(ValueError, "does not match"):
                extract(patch.replace("-int x = 1;", "-int x = 3;"), root)

    def test_path_traversal_and_comment_escape_are_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError, "escapes"):
                extract("--- a/../x.cpp\n+++ b/../x.cpp\n@@ -1 +1 @@\n-// old\n+// new\n", root)
        with self.assertRaises(ValueError):
            render_comment("text */ int evil;", "/* old */")
        with self.assertRaises(ValueError):
            render_comment("text\\", "// old")

    def test_deletions_are_reported_without_inventing_an_added_comment(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "x.cpp").write_text("// old\nint x;\n")
            result = extract("--- a/x.cpp\n+++ b/x.cpp\n@@ -1,2 +1 @@\n-// old\n int x;\n", root)
        self.assertEqual(result["comments"], [])
        self.assertEqual(result["old_comments_touched"], 1)

    def test_judge_requires_coverage_valid_scores_and_real_evidence(self):
        grade = {"label": "C1", **dict.fromkeys(DIMENSIONS, 0), "evidence": [],
                 "explanation": "Direct and accurate.", "missing_facts": [], "unsupported_claims": []}
        validate({"grades": [grade]}, ["C1"], {"C1": "Comment."})
        with self.assertRaises(ValueError):
            validate({"grades": [grade]}, ["C1", "C2"], {"C1": "Comment."})
        with self.assertRaises(ValueError):
            validate({"grades": [{**grade, "meaning": True}]}, ["C1"], {"C1": "Comment."})
        with self.assertRaises(ValueError):
            validate({"grades": [{**grade, "evidence": ["invented"]}]}, ["C1"], {"C1": "Comment."})

    def test_lexical_identity_has_zero_distance(self):
        self.assertTrue(all(value == 0 for value in distance("Only merge live blocks.", "Only merge live blocks.").values()))

    def test_macro_spacing_is_not_treated_as_a_comment_edit(self):
        with self.assertRaisesRegex(ValueError, "Preprocessor"):
            assert_code_preserved("#define F(x) x\n", "#define F (x) x\n")

    def test_quoted_evidence_can_span_source_line_wrapping(self):
        grade = {"label": "C1", **dict.fromkeys(DIMENSIONS, 0), "evidence": ["clear enough"],
                 "explanation": "A line-wrapped quote.", "missing_facts": [], "unsupported_claims": []}
        validate({"grades": [grade]}, ["C1"], {"C1": "clear\n enough"})


if __name__ == "__main__":
    unittest.main()
