"""Deterministic runner and resume checks; no model calls."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from claudish import commits, filelevel, placement
from claudish.corpus import cases as comment_cases
from claudish.io import digest, read_json, write_json
from claudish.runner import MODEL, EFFORT
from claudish.saved import archive_attempt, completed

ROOT = Path(__file__).resolve().parents[1]


def recorded(answer_for):
    def call(prompt, schema, call_dir, *, guidance="", model=MODEL, effort=EFFORT, **options):
        call_dir.mkdir(parents=True)
        (call_dir / "prompt.txt").write_text(prompt)
        (call_dir / "guidance.md").write_text(guidance)
        write_json(call_dir / "schema.json", schema)
        write_json(call_dir / "metadata.json", {
            "status": "completed", "model": model, "reasoning_effort": effort,
            "prompt_sha256": digest(prompt), "guidance_sha256": digest(guidance),
            "schema_sha256": digest(schema), "usage": []})
        answer = answer_for(call_dir)
        write_json(call_dir / "answer.json", answer)
        return answer
    return call


def snapshot(path):
    return {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*") if p.is_file()}


class ResumeRuns(unittest.TestCase):
    def test_placement_resume_reuses_answers_and_refuses_changed_inputs(self):
        corpus = placement.take(placement.cases(ROOT, "train", "corpus/scaled-500"), 2)
        by_id = {case["id"]: case for case in corpus}
        def answer(path):
            needed = by_id[path.parent.name]["expected_needed"]
            return {"needed": needed, "reason": "Fixture.", "comment": "Reason." if needed else ""}
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            spec = Path(tmp) / "spec.md"
            spec.write_text("Frozen spec")
            options = {"corpus_dir": "corpus/scaled-500", "limit": 2, "spec_path": spec}
            with patch("claudish.runner.call", side_effect=recorded(answer)) as calls:
                first = placement.run(ROOT, output, **options)
                self.assertEqual(calls.call_count, 4)
            with patch("claudish.runner.call", side_effect=AssertionError("No calls on resume")):
                self.assertEqual(first, placement.run(ROOT, output, resume=True, **options))
                for changes in ({"model": "other"}, {"effort": "high"}, {"limit": 4}):
                    before = snapshot(output)
                    with self.assertRaisesRegex(ValueError, "Resume input mismatch"):
                        placement.run(ROOT, output, resume=True, **{**options, **changes})
                    self.assertEqual(before, snapshot(output))
                spec.write_text("Changed spec")
                before = snapshot(output)
                with self.assertRaisesRegex(ValueError, "spec_sha256"):
                    placement.run(ROOT, output, resume=True, **options)
                self.assertEqual(before, snapshot(output))
            self.assertEqual(first["with_spec"]["agreement"], 1.0)

    def test_missing_manifest_is_not_a_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "without a saved manifest"):
                placement.run(ROOT, Path(tmp), corpus_dir="corpus/scaled-500", limit=2, resume=True)

    def test_commit_resume_and_offline_rescore(self):
        corpus = commits.cases(ROOT, "train", "corpus/commits")[:2]
        by_id = {case["id"]: case for case in corpus}
        def answer(call_dir):
            case = by_id[call_dir.parent.name]
            path = sorted(case["reference"]["touched_lines"])[0]
            line = case["reference"]["touched_lines"][path][0]
            source = case["sources"][path]
            lines = source.splitlines(keepends=True)
            lines[line - 1] = lines[line - 1].rstrip("\n") + " // fixture\n"
            return {"edits": [{"path": path, "old_text": source, "new_text": "".join(lines)}],
                    "explanation": "Fixture."}
        with tempfile.TemporaryDirectory() as tmp, patch("claudish.commits.cases", return_value=corpus):
            output = Path(tmp) / "run"
            options = {"corpus_dir": "corpus/commits"}
            with patch("claudish.runner.call", side_effect=recorded(answer)):
                summary = commits.run(ROOT, output, **options)
            with patch("claudish.runner.call", side_effect=AssertionError("No calls")):
                self.assertEqual(summary, commits.run(ROOT, output, resume=True, **options))
                self.assertEqual(summary, commits.rescore(output, Path(tmp) / "rescored"))
                for changes in ({"model": "other"}, {"effort": "high"}, {"overlap_threshold": 0.7}):
                    before = snapshot(output)
                    with self.assertRaisesRegex(ValueError, "Resume input mismatch"):
                        commits.run(ROOT, output, resume=True, **{**options, **changes})
                    self.assertEqual(before, snapshot(output))
            self.assertEqual(summary["arms"]["baseline"]["overlaps_real_change"]["passed"], 2)
            self.assertTrue(all(row["shape"]["changed_lines"] == 1
                                for row in read_json(output / "results.json")))


class FileJudgeRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = comment_cases(ROOT, "test", "corpus/scaled")
        cls.corpus = [case for case in corpus if case["path"] == corpus[0]["path"]]
        cls.rubric = (ROOT / "evaluation/file-rubric.md").read_text()

    def rows(self):
        return [{"id": case["id"], "comments": {
            "without_spec": "Baseline fixture.", "with_spec": "Treatment fixture.",
            "upstream": case["reference"]}} for case in self.corpus]

    def answer(self, call_dir):
        path = self.corpus[0]["path"]
        mapping = filelevel.blind_labels(int(digest(f"42:{path}")[:12], 16))
        return {"sets": [{"label": label, "redundancy": 0 if name == "upstream" else 2,
                          "consistency": 0, "proportion": 1, "evidence": [],
                          "explanation": "Fixture."} for label, name in mapping.items()]}

    def test_resume_binds_labels_rubric_model_and_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            write_json(output / "results.json", self.rows())
            write_json(output / "file-judgments.json", {"legacy": True})
            with patch("claudish.filelevel.call", side_effect=recorded(self.answer)) as calls:
                summary = filelevel.judge_run(output, self.corpus, self.rubric)
                self.assertEqual(calls.call_count, 1)
            self.assertEqual(summary["upstream"]["passed"], 1)
            self.assertEqual(summary["with_spec"]["passed"], 0)
            with patch("claudish.filelevel.call", side_effect=AssertionError("No new calls")):
                self.assertEqual(summary, filelevel.judge_run(output, self.corpus, self.rubric, reuse=True))
                for options in ({"seed": 13}, {"model": "other"}, {"min_comments": 2}):
                    before = snapshot(output)
                    with self.assertRaisesRegex(ValueError, "Resume input mismatch"):
                        filelevel.judge_run(output, self.corpus, self.rubric, reuse=True, **options)
                    self.assertEqual(before, snapshot(output))
                before = snapshot(output)
                with self.assertRaisesRegex(ValueError, "rubric_sha256"):
                    filelevel.judge_run(output, self.corpus, self.rubric + "changed", reuse=True)
                self.assertEqual(before, snapshot(output))
                with self.assertRaisesRegex(ValueError, "pass resume"):
                    filelevel.judge_run(output, self.corpus, self.rubric)
                self.assertEqual(before, snapshot(output))
                rows = self.rows()
                rows[0]["comments"]["with_spec"] = "Changed"
                write_json(output / "results.json", rows)
                before = snapshot(output)
                with self.assertRaisesRegex(ValueError, "rows_sha256"):
                    filelevel.judge_run(output, self.corpus, self.rubric, reuse=True)
                self.assertEqual(before, snapshot(output))
            self.assertEqual(read_json(output / "file-judgments.json"), {"legacy": True})

    def test_invalid_judgments_are_preserved_and_excluded_without_rerolling(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            write_json(output / "results.json", self.rows())
            with patch("claudish.filelevel.call", side_effect=recorded(lambda path: {"sets": []})) as calls:
                result = filelevel.judge_run(output, self.corpus, self.rubric)
                self.assertEqual(calls.call_count, 1)
            with patch("claudish.filelevel.call", side_effect=AssertionError("No reroll")):
                self.assertEqual(result, filelevel.judge_run(output, self.corpus, self.rubric, reuse=True))
            self.assertEqual(result["excluded_files"], 1)
            self.assertEqual(result["upstream"]["files"], 0)
            self.assertIn("exactly once", read_json(output / filelevel.JUDGMENTS)["invalid_judgments"][0]["reason"])


class SavedCalls(unittest.TestCase):
    def test_call_inputs_and_artifacts_must_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            call_dir = Path(tmp) / "call"
            recorded(lambda path: {"answer": 1})("prompt", {}, call_dir)
            self.assertEqual(completed(call_dir, "prompt", {}), {"answer": 1})
            for prompt, schema, options in (("other", {}, {}), ("prompt", {"new": 1}, {}),
                                             ("prompt", {}, {"guidance": "other"}),
                                             ("prompt", {}, {"model": "other"})):
                with self.assertRaisesRegex(ValueError, "Saved call input mismatch"):
                    completed(call_dir, prompt, schema, **options)
            (call_dir / "prompt.txt").write_text("modified")
            with self.assertRaisesRegex(ValueError, "prompt.txt"):
                completed(call_dir, "prompt", {})

    def test_retry_archives_the_entire_failed_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            call_dir = Path(tmp) / "call"
            recorded(lambda path: {"answer": 1})("prompt", {}, call_dir)
            metadata = read_json(call_dir / "metadata.json")
            write_json(call_dir / "metadata.json", {**metadata, "status": "failed"})
            self.assertIsNone(completed(call_dir, "prompt", {}))
            archive_attempt(call_dir)
            self.assertFalse(call_dir.exists())
            archived, = (Path(tmp) / "attempts").iterdir()
            self.assertEqual(read_json(archived / "answer.json"), {"answer": 1})


if __name__ == "__main__":
    unittest.main()
