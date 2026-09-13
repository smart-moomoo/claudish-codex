"""The three new runners, driven end to end from saved calls instead of a model.

Every call directory is pre-filled with a completed answer, so these exercise
prompt assembly, validation, scoring, reporting and manifests without needing
Codex and without spending anything.
"""

from pathlib import Path
import tempfile
import unittest

from claudish import commits, filelevel, placement
from claudish.corpus import cases as comment_cases
from claudish.io import digest, read_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def unique_anchor(text, line):
    """A snippet around a line that occurs exactly once, so an edit can apply.

    A touched line is often blank or repeated; widening until the snippet is
    unique is what a model has to do to name an edit site at all.
    """
    lines = text.splitlines(keepends=True)
    for width in range(0, 8):
        start = max(0, line - 1 - width)
        snippet = "".join(lines[start:line + width])
        if snippet.strip() and text.count(snippet) == 1:
            return snippet
    raise AssertionError(f"No unique anchor near line {line}")


def save_call(call_dir, answer):
    call_dir.mkdir(parents=True, exist_ok=True)
    write_json(call_dir / "metadata.json", {"status": "completed", "model": "gpt-5.6-sol",
                                            "reasoning_effort": "medium", "usage": []})
    write_json(call_dir / "answer.json", answer)


class PlacementRun(unittest.TestCase):
    def test_decisions_are_scored_against_what_llvm_did(self):
        corpus = placement.cases(ROOT, "train", "corpus/scaled-500")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "placement"
            for case in corpus:
                for arm in placement.ARMS:
                    # One arm always asks for a comment; the other answers correctly.
                    needed = True if arm == "without_spec" else case["expected_needed"]
                    save_call(output / "calls" / case["id"] / arm,
                              {"needed": needed, "reason": "Recorded for this test.",
                               "comment": "Explains the invariant." if needed else ""})
            summary = placement.run(ROOT, output, split="train",
                                    corpus_dir="corpus/scaled-500", resume=True)
            manifest = read_json(output / "manifest.json")
            decisions = read_json(output / "decisions.json")
            report = (output / "report.md").read_text()
        self.assertEqual(manifest["status"], "completed")
        self.assertIn("Disagreements", report)
        self.assertEqual(len(decisions), 2 * len(corpus))
        self.assertTrue(summary["without_spec"]["always_says_yes"])
        self.assertEqual(summary["without_spec"]["discrimination"], 0.0)
        self.assertEqual(summary["with_spec"]["agreement"], 1.0)

    def test_an_existing_directory_is_refused_without_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "pass resume"):
                placement.run(ROOT, Path(tmp), split="train", corpus_dir="corpus/scaled-500")


class FileJudgeRun(unittest.TestCase):
    def setUp(self):
        self.corpus = comment_cases(ROOT, "test", "corpus/scaled")
        self.rubric = (ROOT / "evaluation/file-rubric.md").read_text()

    def rows(self):
        return [{"id": case["id"], "comments": {
            "without_spec": f"Baseline note for {case['id']}.",
            "with_spec": f"Treatment note for {case['id']}.",
            "upstream": case["reference"]}} for case in self.corpus]

    def test_each_file_is_judged_once_and_scored_per_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            output.mkdir()
            write_json(output / "results.json", self.rows())
            files = filelevel.group(self.rows(), self.corpus)
            for path in files:
                mapping = filelevel.blind_labels(int(digest(f"42:{path}")[:12], 16))
                save_call(output / "file-calls" / digest(path)[:16], {"sets": [
                    {"label": label, "redundancy": 0 if name == "upstream" else 2,
                     "consistency": 0, "proportion": 1, "evidence": [],
                     "explanation": "Recorded for this test."}
                    for label, name in mapping.items()]})
            summary = filelevel.judge_run(output, self.corpus, self.rubric, reuse=True)
            saved = read_json(output / "file-judgments.json")
        self.assertEqual(summary["upstream"]["files"], len(files))
        self.assertEqual(summary["upstream"]["passed"], len(files))
        # A noticeable deficit fails the criterion even when the others are clean.
        self.assertEqual(summary["with_spec"]["passed"], 0)
        self.assertEqual(summary["with_spec"]["redundancy"], 2)
        by_arm = {(item["path"], item["arm"]) for item in saved["files"]}
        self.assertEqual(len(by_arm), len(files) * len(filelevel.SETS))

    def test_a_judge_answer_missing_a_set_stops_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            output.mkdir()
            write_json(output / "results.json", self.rows())
            for path in filelevel.group(self.rows(), self.corpus):
                save_call(output / "file-calls" / digest(path)[:16], {"sets": []})
            with self.assertRaisesRegex(ValueError, "each set exactly once"):
                filelevel.judge_run(output, self.corpus, self.rubric, reuse=True)


class CommitRun(unittest.TestCase):
    def test_answers_are_compared_with_the_real_commit(self):
        corpus = commits.cases(ROOT, "train", "corpus/commits")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "patches"
            for case in corpus:
                path = sorted(case["reference"]["touched_lines"])[0]
                line = case["reference"]["touched_lines"][path][0]
                old = unique_anchor(case["sources"][path], line)
                save_call(output / "calls" / case["id"] / "baseline",
                          {"edits": [{"path": path, "old_text": old,
                                      "new_text": old.rstrip("\n") + " // touched\n"}],
                           "explanation": "Recorded for this test."})
            summary = commits.run(ROOT, output, split="train",
                                  corpus_dir="corpus/commits", resume=True)
            results = read_json(output / "results.json")
            manifest = read_json(output / "manifest.json")
        self.assertEqual(manifest["arms"], ["baseline"])
        self.assertEqual(len(results), len(corpus))
        # Every answer edits a line the real commit also changed.
        self.assertEqual(summary["arms"]["baseline"]["applies"]["passed"], len(corpus))
        self.assertEqual(summary["arms"]["baseline"]["overlaps_real_change"]["passed"], len(corpus))
        self.assertTrue(all(row["comparison"]["region_overlap"] > 0 for row in results))

    def test_an_answer_that_does_nothing_never_reaches_a_shape_measure(self):
        corpus = commits.cases(ROOT, "train", "corpus/commits")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "patches"
            for case in corpus:
                save_call(output / "calls" / case["id"] / "baseline",
                          {"edits": [], "explanation": "Nothing to change."})
            summary = commits.run(ROOT, output, split="train",
                                  corpus_dir="corpus/commits", resume=True)
        self.assertEqual(summary["arms"]["baseline"]["applies"]["passed"], 0)
        self.assertEqual(summary["arms"]["baseline"]["invasive"]["judged"], 0)


if __name__ == "__main__":
    unittest.main()
