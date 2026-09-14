"""Scoped review contracts with synthetic fixtures and no model calls."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from claudish import changes, spec
from claudish.io import digest, read_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def change():
    return {"task": "Simplify the implementation and update its explanation.",
            "artifacts": [{"id": kind, "kind": kind, "path": f"fixture/{kind}",
                           "before": "original", "after": "replacement", "context": "surrounding context"}
                          for kind in changes.APPLIES]}


def answer():
    grade = {"deficit": 0, "explanation": "Synthetic assessment.", "evidence": []}
    return {"artifacts": [{"id": item["id"], "blockers": [],
                           **{name: deepcopy(grade) if name in changes.APPLIES[item["kind"]] else None
                              for name in changes.CRITERIA}} for item in change()["artifacts"]]}


class ReviewScope(unittest.TestCase):
    def test_only_comments_have_four_applicable_criteria(self):
        result = changes.summarize(answer(), change())
        by_kind = {item["kind"]: item for item in result["artifacts"]}
        for kind in changes.APPLIES:
            for name in changes.CRITERIA:
                expected = "pass" if name in changes.APPLIES[kind] else "not_applicable"
                self.assertEqual(by_kind[kind]["criteria"][name]["status"], expected)
        self.assertEqual(result["by_kind"]["code"]["criteria"]["clean"]["pass"], 0)
        self.assertEqual(result["correctness"], "not_established")

    def test_comment_failure_does_not_hide_code_review(self):
        raw = answer()
        raw["artifacts"][0]["clean"].update(deficit=3, evidence=[
            {"artifact_id": "comment", "source": "after", "quote": "replacement"}])
        result = changes.summarize(raw, change())
        by_kind = {item["kind"]: item for item in result["artifacts"]}
        self.assertEqual(by_kind["comment"]["outcome"], "fail")
        self.assertEqual(by_kind["code"]["outcome"], "criteria_passed")
        self.assertEqual(by_kind["comment"]["criteria"]["optimal"]["status"], "pass")

    def test_unassessed_is_not_not_applicable_or_pass(self):
        raw = answer()
        raw["artifacts"][2]["optimal"].update(deficit=None, explanation="Caller context is missing.")
        result = changes.summarize(raw, change())
        code = result["artifacts"][2]
        self.assertEqual(code["outcome"], "unassessed")
        self.assertEqual(code["criteria"]["clean"]["status"], "not_applicable")
        self.assertEqual(code["criteria"]["optimal"]["status"], "unassessed")

    def test_blockers_prevent_a_criteria_pass_outcome(self):
        raw = answer()
        raw["artifacts"][2]["blockers"] = ["Synthetic task-completion problem."]
        result = changes.summarize(raw, change())
        self.assertEqual(result["artifacts"][2]["outcome"], "blocked")

    def test_non_comment_clean_scores_and_missing_comment_scores_are_refused(self):
        raw = answer()
        raw["artifacts"][1]["clean"] = deepcopy(raw["artifacts"][0]["clean"])
        with self.assertRaisesRegex(ValueError, "not applicable"):
            changes.validate_answer(raw, change())
        raw = answer()
        raw["artifacts"][0]["effective"] = None
        with self.assertRaisesRegex(ValueError, "applicable assessment"):
            changes.validate_answer(raw, change())

    def test_exact_coverage_types_and_evidence(self):
        for mutate in (
            lambda raw: raw["artifacts"].pop(),
            lambda raw: raw["artifacts"].append(deepcopy(raw["artifacts"][0])),
            lambda raw: raw["artifacts"][0]["clean"].update(deficit=True),
            lambda raw: raw["artifacts"][0]["clean"].update(deficit=5),
            lambda raw: raw["artifacts"][0]["clean"].update(deficit=2),
        ):
            raw = answer()
            mutate(raw)
            with self.assertRaises(ValueError):
                changes.validate_answer(raw, change())
        raw = answer()
        evidence = {"artifact_id": "text", "source": "before", "quote": "original"}
        raw["artifacts"][2]["optimal"].update(deficit=2, evidence=[evidence])
        changes.validate_answer(raw, change())
        evidence["quote"] = "fabricated"
        with self.assertRaisesRegex(ValueError, "quote"):
            changes.validate_answer(raw, change())

    def test_input_kinds_are_explicit_and_no_ops_remain_reviewable(self):
        data = change()
        data["artifacts"][0]["after"] = data["artifacts"][0]["before"]
        changes.validate_input(data)
        data["artifacts"][0]["kind"] = "mixed"
        with self.assertRaisesRegex(ValueError, "kind"):
            changes.validate_input(data)
        data = change()
        data["artifacts"][1]["id"] = data["artifacts"][0]["id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            changes.validate_input(data)


class ReviewRunner(unittest.TestCase):
    def test_review_records_inputs_and_refuses_to_overwrite_existing_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path, output = Path(tmp) / "input.json", Path(tmp) / "review"
            write_json(input_path, change())
            with patch("claudish.changes.call", return_value=answer()) as call:
                result = changes.review(ROOT, input_path, output)
                self.assertEqual(call.call_count, 1)
                self.assertEqual(call.call_args.kwargs["model"], "gpt-5.6-sol")
                self.assertEqual(call.call_args.kwargs["effort"], "medium")
                self.assertNotIn("guidance", call.call_args.kwargs)
                self.assertEqual(read_json(output / "manifest.json")["input_sha256"], digest(change()))
                self.assertEqual(result, read_json(output / "review.json"))
                with self.assertRaises(FileExistsError):
                    changes.review(ROOT, input_path, output)
                self.assertEqual(call.call_count, 1)

    def test_invalid_raw_answer_is_preserved_without_retry(self):
        def saved_invalid(prompt, schema, call_dir, **options):
            write_json(call_dir / "answer.json", {"artifacts": []})
            return {"artifacts": []}
        with tempfile.TemporaryDirectory() as tmp:
            input_path, output = Path(tmp) / "input.json", Path(tmp) / "review"
            write_json(input_path, change())
            with patch("claudish.changes.call", side_effect=saved_invalid) as call:
                with self.assertRaisesRegex(ValueError, "every artifact"):
                    changes.review(ROOT, input_path, output)
                self.assertEqual(call.call_count, 1)
            self.assertEqual(read_json(output / "manifest.json")["status"], "failed")
            self.assertEqual(read_json(output / "call/answer.json"), {"artifacts": []})
            self.assertFalse((output / "review.json").exists())


class GeneratedScope(unittest.TestCase):
    def test_shared_guidance_changes_do_not_change_the_comment_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "specs").mkdir()
            for name in ("base.md", "changes-base.md"):
                (root / "specs" / name).write_text((ROOT / "specs" / name).read_text())
            entries = read_json(ROOT / "dictionary/entries.json")
            for item in entries:
                item["evidence"] = ["https://example.com/synthetic-test-fixture"]
            write_json(root / "dictionary/entries.json", entries)
            before = spec.build(root)
            self.assertEqual(before["sha256"], digest((ROOT / "specs/codex-comments.md").read_text()))
            path = root / "specs/changes-base.md"
            path.write_text(path.read_text() + "\nSynthetic test instruction.\n")
            with self.assertRaisesRegex(ValueError, "stale"):
                spec.build(root, check=True)
            after = spec.build(root)
            self.assertEqual(before["sha256"], after["sha256"])
            self.assertNotEqual(before["changes_sha256"], after["changes_sha256"])
            spec.build(root, check=True)


if __name__ == "__main__":
    unittest.main()
