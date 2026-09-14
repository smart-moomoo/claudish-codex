"""Judging a file's comments as a set rather than one at a time."""

from pathlib import Path
import unittest
from unittest.mock import patch

from claudish.corpus import cases
from claudish.cpp import scan
from claudish.filelevel import SETS, blind_labels, group, payload, validate

ROOT = Path(__file__).resolve().parents[1]


def row(case, text):
    return {"id": case["id"], "comments": {"without_spec": text, "with_spec": text,
                                           "upstream": case["reference"]}}


class Grouping(unittest.TestCase):
    def setUp(self):
        self.corpus = cases(ROOT, "test", "corpus/scaled")

    def test_a_file_without_enough_comments_cannot_form_a_set(self):
        files = group([row(case, "note") for case in self.corpus], self.corpus, min_comments=3)
        self.assertTrue(files)
        for path, items in files.items():
            self.assertGreaterEqual(len(items), 3)
            self.assertEqual([case["line"] for case, _ in items],
                             sorted(case["line"] for case, _ in items))
        self.assertEqual(group([row(self.corpus[0], "note")], self.corpus, min_comments=2), {})

    def test_every_set_answers_the_same_locations_with_the_code_shown_once(self):
        files = group([row(case, "note") for case in self.corpus], self.corpus)
        items = next(iter(files.values()))
        locations, sets = payload(items)
        self.assertEqual(set(sets), set(SETS))
        for entries in sets.values():
            self.assertEqual([item["location"] for item in entries],
                             [item["location"] for item in locations])
        self.assertTrue(all(item["code_after_comment"].strip() for item in locations))

    def test_a_row_with_no_corpus_case_is_refused(self):
        with self.assertRaisesRegex(ValueError, "no corpus case"):
            group([{"id": "missing", "comments": {}}], self.corpus, min_comments=1)

    def test_code_starts_after_the_comment_and_hides_nearby_references(self):
        source = "// first reference\n// continued\nint value = 1;\n// next reference\nuse(value);\n"
        case = {"id": "x", "source": source, "line": 1,
                "end": source.index("int value"), "reference": "first reference continued"}
        locations, _ = payload([(case, row(case, "generated"))])
        self.assertEqual(locations[0]["code_after_comment"], "int value = 1;\nuse(value);")

    def test_block_comment_before_code_on_the_same_line(self):
        source = "/* reference */ int value;\n"
        case = {"id": "x", "source": source, "line": 1,
                "end": source.index("*/") + 2, "reference": "reference"}
        locations, _ = payload([(case, row(case, "generated"))])
        self.assertEqual(locations[0]["code_after_comment"], " int value;")


class SharedContext(unittest.TestCase):
    def test_each_distinct_source_is_scanned_once_without_caching_across_calls(self):
        source = "// first\nint first;\n// second\nint second;\n"
        comments, _ = scan(source)
        items = []
        for index, comment in enumerate(comments):
            case = {"id": str(index), "source": source, "line": comment.line,
                    "end": comment.end, "reference": comment.text}
            items.append((case, row(case, "fixture")))
        with patch("claudish.filelevel.scan", wraps=scan) as scanner:
            locations, _ = payload(items)
            self.assertEqual(scanner.call_count, 1)
            self.assertEqual(locations[0]["code_after_comment"], "int first;\nint second;")
            self.assertEqual(locations[1]["code_after_comment"], "int second;")
            payload(items)
            self.assertEqual(scanner.call_count, 2)
        other = {**items[1][0], "source": source.replace("int second;", "int changed;")}
        with patch("claudish.filelevel.scan", wraps=scan) as scanner:
            locations, _ = payload([items[0], (other, row(other, "fixture"))])
            self.assertEqual(scanner.call_count, 2)
            self.assertEqual(locations[1]["code_after_comment"], "int changed;")


class Blinding(unittest.TestCase):
    def test_labels_cover_every_set_and_follow_only_the_seed(self):
        first, again = blind_labels(7), blind_labels(7)
        self.assertEqual(first, again)
        self.assertEqual(sorted(first.values()), sorted(SETS))
        self.assertNotEqual(blind_labels(7), blind_labels(8))


class Validation(unittest.TestCase):
    def setUp(self):
        self.mapping = {"S1": "without_spec", "S2": "with_spec", "S3": "upstream"}
        self.texts = {label: f"comment text for {name}" for label, name in self.mapping.items()}

    def answer(self, **overrides):
        sets = [{"label": label, "redundancy": 0, "consistency": 0, "proportion": 0,
                 "evidence": [], "explanation": "Fine.", **overrides.pop(label, {})}
                for label in self.mapping]
        return {"sets": sets, **overrides}

    def test_a_complete_answer_is_accepted(self):
        self.assertEqual(len(validate(self.answer(), self.mapping, self.texts)), 3)

    def test_non_object_sets_are_invalid(self):
        with self.assertRaisesRegex(ValueError, "Malformed file judge set"):
            validate({"sets": [None]}, self.mapping, self.texts)

    def test_a_set_left_ungraded_is_refused(self):
        answer = self.answer()
        answer["sets"] = answer["sets"][:2]
        with self.assertRaisesRegex(ValueError, "each set exactly once"):
            validate(answer, self.mapping, self.texts)

    def test_scores_outside_the_scale_and_unexplained_scores_are_refused(self):
        with self.assertRaisesRegex(ValueError, "Invalid file judge grade"):
            validate(self.answer(S1={"redundancy": 9}), self.mapping, self.texts)
        with self.assertRaisesRegex(ValueError, "must explain"):
            validate(self.answer(S2={"explanation": "  "}), self.mapping, self.texts)

    def test_evidence_must_be_quoted_from_the_set_it_grades(self):
        with self.assertRaisesRegex(ValueError, "must occur in the set"):
            validate(self.answer(S1={"evidence": ["text for with_spec"]}),
                     self.mapping, self.texts)
        validate(self.answer(S1={"evidence": ["comment text  for without_spec"]}),
                 self.mapping, self.texts)


if __name__ == "__main__":
    unittest.main()
