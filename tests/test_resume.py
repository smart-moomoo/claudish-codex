"""Continuing an interrupted run without repeating work already paid for."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from claudish.corpus import cases
from claudish.experiment import _completed, _generate_one, resume
from claudish.io import digest, write_json
from claudish.judge import DIMENSIONS, blind_labels

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "corpus/long-blocks"
SPEC, RUBRIC, TASK = "Write plainly.\n", "Grade them.\n", "Write the comment.\n"
ARMS = ("without_spec", "with_spec")


def comment_for(case, arm):
    return f"{arm} comment for {case['id']}, stated plainly."


def save_call(call_dir, answer):
    call_dir.mkdir(parents=True, exist_ok=True)
    write_json(call_dir / "metadata.json", {"status": "completed", "model": "gpt-5.6-sol",
                                            "reasoning_effort": "medium", "usage": []})
    write_json(call_dir / "answer.json", answer)


def judge_answer(case, comments, seed, judge_index):
    blind_seed = int(digest(f"{seed}:{case['id']}:0:{judge_index}")[:12], 16)
    mapping = blind_labels(comments, blind_seed)
    return {"grades": [{"label": label, **dict.fromkeys(DIMENSIONS, 1), "evidence": [],
                        "explanation": "Scored.", "missing_facts": [], "unsupported_claims": []}
                       for label in mapping]}


def build_interrupted_run(output, corpus, *, seed=42, judges=2, skip_last_judge=True):
    output.mkdir(parents=True, exist_ok=True)
    (output / "spec.md").write_text(SPEC)
    (output / "rubric.md").write_text(RUBRIC)
    (output / "task.md").write_text(TASK)
    write_json(output / "manifest.json", {
        "name": "fixture", "status": "running", "split": "train", "repeats": 1,
        "judges_per_pair": judges, "model": "gpt-5.6-sol", "effort": "medium", "seed": seed,
        "spec_sha256": digest(SPEC), "rubric_sha256": digest(RUBRIC), "task_sha256": digest(TASK),
        "cases_sha256": digest(json.loads((DATA / "cases.json").read_text())),
        "source_lock_sha256": digest(json.loads((DATA / "sources.lock.json").read_text())),
        "corpus_dir": str(DATA), "case_ids": [case["id"] for case in corpus]})
    for case in corpus:
        comments = {arm: comment_for(case, arm) for arm in ARMS}
        comments["upstream"] = case["reference"]
        for arm in ARMS:
            save_call(output / "calls" / f"{case['id']}-0" / arm, {"comment": comments[arm]})
        for index in range(judges):
            if skip_last_judge and case is corpus[-1] and index == judges - 1:
                continue
            save_call(output / "calls" / f"{case['id']}-0" / f"judge-{index}",
                      judge_answer(case, comments, seed, index))


class ResumeReusesCompletedCalls(unittest.TestCase):
    def setUp(self):
        self.corpus = cases(ROOT, "train", "corpus/long-blocks")

    def test_a_fully_saved_run_finishes_with_no_further_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            build_interrupted_run(output, self.corpus, skip_last_judge=False)
            before = {p: p.read_bytes() for p in output.glob("calls/*/*/metadata.json")}
            summary = resume(output)
            after = {p: p.read_bytes() for p in output.glob("calls/*/*/metadata.json")}
            manifest = json.loads((output / "manifest.json").read_text())
        # Identical metadata proves nothing was sent to the model again.
        self.assertEqual(before, after)
        self.assertEqual(summary["pairs"], len(self.corpus))
        self.assertEqual(summary["valid_judgments"], 2 * len(self.corpus))
        self.assertEqual(manifest["status"], "completed")
        self.assertEqual(manifest["previous_status"], "running")

    def test_an_unfinished_call_is_not_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            build_interrupted_run(output, self.corpus)
            case = self.corpus[0]
            call_dir = output / "calls" / f"{case['id']}-0" / "without_spec"
            self.assertIsNotNone(_completed(call_dir))
            write_json(call_dir / "metadata.json", {"status": "running"})
            self.assertIsNone(_completed(call_dir))

    def test_a_completed_generation_returns_its_saved_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            build_interrupted_run(output, self.corpus)
            case = self.corpus[0]
            before = (output / "calls" / f"{case['id']}-0" / "without_spec" / "metadata.json").read_bytes()
            key, text, invalid = _generate_one(case, "without_spec", 0, output=output, task=TASK,
                                               spec="", options={"timeout": 1}, reuse=True)
            after = (output / "calls" / f"{case['id']}-0" / "without_spec" / "metadata.json").read_bytes()
        self.assertEqual(before, after)
        self.assertEqual(text, comment_for(case, "without_spec"))
        self.assertIsNone(invalid)

    def test_a_finished_run_and_a_changed_input_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            build_interrupted_run(output, self.corpus, skip_last_judge=False)
            manifest = json.loads((output / "manifest.json").read_text())
            write_json(output / "manifest.json", {**manifest, "status": "completed"})
            with self.assertRaisesRegex(ValueError, "interrupted or failed"):
                resume(output)
            write_json(output / "manifest.json", manifest)
            (output / "rubric.md").write_text("A different rubric.\n")
            with self.assertRaisesRegex(ValueError, "rubric_sha256"):
                resume(output)

    def test_changed_source_lock_is_refused_before_any_call(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            build_interrupted_run(output, self.corpus, skip_last_judge=False)
            manifest = json.loads((output / "manifest.json").read_text())
            write_json(output / "manifest.json", {**manifest, "source_lock_sha256": "changed"})
            with patch("claudish.experiment.call", side_effect=AssertionError("No model calls")):
                with self.assertRaisesRegex(ValueError, "Source lock changed"):
                    resume(output)


if __name__ == "__main__":
    unittest.main()
