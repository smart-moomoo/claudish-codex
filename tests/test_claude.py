"""Claude isolation, whole-change editing, provenance and resume contracts."""

from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from claudish import claude_cases as cases, claude_experiment as experiment, claude_runner as runner, claude_spec
from claudish import claude_review
from claudish.io import digest, read_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def case():
    return {"id": "fixture", "split": "train", "task": "Preserve the result and explain it directly.",
            "provenance": {"authorship": "synthetic", "repository": "fixture"},
            "files": [{"path": "a.py", "kind": "code", "before": "def f():\n    return 1\n",
                       "input": "def f():\n    # The actual result is one.\n    return 1\n"}],
            "context": {"test_a.py": "assert f() == 1\n"}}


def events(**start_updates):
    start = {"type": "system", "subtype": "init", "session_id": "fresh", "model": runner.MODEL,
             "tools": ["StructuredOutput"], "mcp_servers": [], "skills": [], "plugins": []}
    start.update(start_updates)
    result = {"type": "result", "subtype": "success", "session_id": "fresh", "is_error": False,
              "modelUsage": {runner.MODEL: {"inputTokens": 12}},
              "structured_output": {"edits": [], "explanation": "Already sufficient."}}
    return "\n".join(json.dumps(e) for e in (start, result))


class Isolation(unittest.TestCase):
    def test_model_tools_customizations_and_session_are_checked(self):
        runner.parse_events(events(), runner.MODEL)
        builtin = {"name": "agents-md", "path": "builtin", "source": "agents-md@builtin"}
        runner.parse_events(events(plugins=[builtin]), runner.MODEL)
        for kwargs in ({"model": "other"}, {"tools": ["Bash"]}, {"skills": ["personal"]},
                       {"plugins": [{**builtin, "path": "/personal"}]}, {"mcp_servers": [{}]},
                       {"session_id": "other"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                runner.parse_events(events(**kwargs), runner.MODEL)
        with self.assertRaisesRegex(ValueError, "model usage"):
            runner.parse_events(events().replace(
                '"modelUsage": {"' + runner.MODEL, '"modelUsage": {"other'), runner.MODEL)

    def test_real_command_contract_and_private_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "call"
            def execute(command, **options):
                self.assertEqual(command[command.index("--model") + 1], runner.MODEL)
                for flag in ("--safe-mode", "--no-session-persistence", "--strict-mcp-config", "--disable-slash-commands"):
                    self.assertIn(flag, command)
                self.assertEqual(command[command.index("--tools") + 1], "")
                self.assertEqual(command[command.index("--setting-sources") + 1], "")
                self.assertNotIn("PRIVATE_TEST_VALUE", options["env"])
                self.assertNotIn("ANTHROPIC_BASE_URL", options["env"])
                self.assertNotIn("--resume", command)
                self.assertEqual(list(Path(options["cwd"]).iterdir()), [])
                return subprocess.CompletedProcess(command, 0, events(), "")
            with patch.dict("os.environ", {"PRIVATE_TEST_VALUE": "not-for-model", "ANTHROPIC_BASE_URL": "https://other.invalid"}), \
                 patch("claudish.claude_runner.shutil.which", return_value="claude"), \
                 patch("claudish.claude_runner.subprocess.check_output", return_value="fixture-version"), \
                 patch("claudish.claude_runner.subprocess.run", side_effect=execute):
                result = runner.call("task", cases.SCHEMA, target)
            self.assertEqual(read_json(target / "metadata.json")["answer_sha256"], digest(result))
            with self.assertRaises(FileExistsError):
                runner.call("task", cases.SCHEMA, target)

    def test_timeout_preserves_partial_events(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch("claudish.claude_runner.shutil.which", return_value="claude"), \
             patch("claudish.claude_runner.subprocess.check_output", return_value="fixture-version"), \
             patch("claudish.claude_runner.subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 1, output=b"partial", stderr=b"error")):
            target = Path(tmp) / "call"
            with self.assertRaises(subprocess.TimeoutExpired):
                runner.call("task", cases.SCHEMA, target)
            self.assertEqual((target / "events.jsonl").read_text(), "partial")
            self.assertEqual(read_json(target / "metadata.json")["status"], "failed")


class WholeChanges(unittest.TestCase):
    def test_export_preserves_a_whole_large_commit_and_refuses_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "case.json"
            repo = Path(tmp) / "repo"
            repo.mkdir()
            def git(*args):
                return subprocess.check_output(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL)
            git("init")
            (repo / "f0.py").write_text("VALUE = 0\n")
            git("add", "f0.py")
            git("commit", "-m", "Synthetic parent")
            for index in range(12):
                (repo / f"f{index}.py").write_text("".join(f"VALUE_{n} = {n}\n" for n in range(60)))
            git("add", ".")
            git("commit", "-m", "Synthetic large change")
            revision = git("rev-parse", "HEAD").strip()
            with self.assertRaisesRegex(ValueError, "exceeds byte limit"):
                cases.export(repo, revision, target, case_id="large", split="train", max_bytes=10)
            self.assertFalse(target.exists())
            result = cases.export(repo, revision, target, case_id="large", split="train")
            self.assertEqual(result["band"], "large")
            self.assertEqual(result["files"], 12)
            exported = read_json(target)
            names = git("diff", "--name-only", revision + "^", revision).splitlines()
            self.assertEqual(sorted(f["path"] for f in exported["files"]), sorted(names))
            for item in exported["files"]:
                self.assertEqual(item["input"], git("show", revision + ":" + item["path"]))
            with self.assertRaises(FileExistsError):
                cases.export(repo, revision, target, case_id="large", split="train")

    def test_noop_and_exact_nonoverlapping_edits(self):
        data = cases.validate(case())
        unchanged = {f["path"]: f["input"] for f in data["files"]}
        self.assertEqual(cases.apply({"edits": [], "explanation": "No change needed."}, data), unchanged)
        answer = {"edits": [{"path": "a.py", "old_text": "# The actual result is one.", "new_text": "# Return one."}], "explanation": "Direct wording."}
        result = cases.apply(answer, data)
        self.assertIn("# Return one.", result["a.py"])
        for bad in (
            {"path": "../secret", "old_text": "x", "new_text": "y"},
            {"path": "test_a.py", "old_text": "assert", "new_text": "pass"},
            {"path": "a.py", "old_text": "", "new_text": "new"},
            {"path": "a.py", "old_text": "return", "new_text": None},
        ):
            with self.assertRaises(ValueError):
                cases.apply({"edits": [bad], "explanation": ""}, data)
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            cases.apply({"edits": answer["edits"] * 2, "explanation": ""}, data)

    def test_creation_deletion_and_empty_files(self):
        data = case()
        data["files"] += [{"path": "removed.py", "kind": "code", "before": "old", "input": None},
                          {"path": "empty.txt", "kind": "text", "before": None, "input": ""}]
        edits = [{"path": "removed.py", "old_text": "", "new_text": "restored"},
                 {"path": "empty.txt", "old_text": "", "new_text": "added"},
                 {"path": "a.py", "old_text": data["files"][0]["input"], "new_text": None}]
        self.assertEqual(cases.apply({"edits": edits, "explanation": ""}, data),
                         {"a.py": None, "removed.py": "restored", "empty.txt": "added"})

    def test_split_checks_include_context_and_entire_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.json", Path(tmp) / "b.json"
            first, second = case(), case()
            second.update(id="heldout", split="test")
            second["files"][0]["path"] = "b.py"
            write_json(a, first)
            write_json(b, second)
            with self.assertRaisesRegex(ValueError, "crosses splits"):
                cases.load([a, b], "train")
        for name in ("../escape", "/absolute", "a/../b", ".git/config", "a\\b"):
            with self.assertRaises(ValueError):
                cases.path_name(name)

    def test_full_file_and_comment_review_scope(self):
        data = case()
        result = experiment.review_input(data, {"a.py": data["files"][0]["input"]})
        self.assertEqual([a["kind"] for a in result["artifacts"]], ["code", "comment"])
        self.assertEqual(result["artifacts"][0]["before"], data["files"][0]["input"])
        self.assertIn("assert f() == 1", result["task"])

    def test_python_diagnostics_do_not_confuse_docstrings_with_logic(self):
        data = case()
        same = {"a.py": 'def f():\n    """Return one."""\n    return 1\n'}
        self.assertEqual(experiment.code_diagnostics(data, same)["python_ast_changed"], [])
        changed = {"a.py": "def f():\n    return 2\n"}
        self.assertEqual(experiment.code_diagnostics(data, changed)["python_ast_changed"], ["a.py"])
        broken = {"a.py": "def f(:\n"}
        self.assertEqual(experiment.code_diagnostics(data, broken)["introduced_python_syntax_errors"], ["a.py"])


class Study(unittest.TestCase):
    def test_review_records_transport_and_rejects_inexact_evidence(self):
        data = {"task": "Preserve meaning.", "artifacts": [
            {"id": "a", "kind": "text", "path": "a.md", "before": "Original text.",
             "after": "Direct text.", "context": ""}]}
        grade = {"deficit": 0, "explanation": "Synthetic assessment.", "evidence": []}
        answer = {"artifacts": [{"id": "a", "clean": None, "effective": None,
                                 "invasive": deepcopy(grade), "optimal": deepcopy(grade), "blockers": []}]}
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.json"
            write_json(source, data)
            with patch("claudish.claude_review.call", return_value=answer) as call:
                result = claude_review.review(ROOT, source, tmp / "valid")
            self.assertEqual(result["artifacts"][0]["outcome"], "criteria_passed")
            self.assertEqual(call.call_args.kwargs["effort"], "medium")
            manifest = read_json(tmp / "valid/manifest.json")
            self.assertEqual(manifest["status"], "completed")
            self.assertEqual(manifest["encoding"], "literal")
            self.assertEqual(manifest["prompt_sha256"], digest(call.call_args.args[0]))
            answer["artifacts"][0]["invasive"]["evidence"] = [
                {"artifact_id": "a", "source": "after", "quote": "Invented quote."}]
            with patch("claudish.claude_review.call", return_value=answer), self.assertRaisesRegex(ValueError, "exactly"):
                claude_review.review(ROOT, source, tmp / "invalid")
            self.assertEqual(read_json(tmp / "invalid/manifest.json")["status"], "failed")
            self.assertEqual(read_json(tmp / "invalid/input.json"), data)
            self.assertFalse((tmp / "invalid/review.json").exists())

    def test_large_review_encoding_is_lossless_and_does_not_crop(self):
        text = "Long, repeated source text.\n" * 400
        data = {"task": "Review the complete document.", "artifacts": [
            {"id": "a", "kind": "text", "path": "a.md", "before": text, "after": text, "context": ""}]}
        packed = claude_review.pack(data)
        self.assertEqual(claude_review.unpack(packed), data)
        prompt, encoding = claude_review.prompt_for(data, "Fixed rubric", max_chars=15000)
        self.assertEqual(encoding, "interned-exact-text-v1")
        self.assertIn(json.dumps(text), prompt)
        with self.assertRaisesRegex(ValueError, "no content was truncated"):
            claude_review.prompt_for(data, "Fixed rubric", max_chars=100)
        _, encoding = claude_review.prompt_for(data, "Fixed rubric")
        self.assertEqual(encoding, "literal")

    def test_reuse_failures_and_provenance_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source, output = tmp / "case.json", tmp / "run"
            write_json(source, case())
            def call(prompt, schema, target, **options):
                self.assertNotIn('"provenance"', prompt)
                self.assertNotIn('"split"', prompt)
                self.assertIn('"complete_patch"', prompt)
                if options["guidance"] == "":
                    raise ValueError("Preserved synthetic failure")
                return {"edits": [], "explanation": "Synthetic no-op"}
            with patch("claudish.claude_runner.call", side_effect=call) as calls:
                first = experiment.run(ROOT, [source], output, judge=False)
                self.assertEqual(calls.call_count, 3)
                self.assertEqual(first["failed"], 1)
            with patch("claudish.claude_runner.call", side_effect=AssertionError("Do not reroll")):
                self.assertEqual(first, experiment.run(ROOT, [source], output, judge=False, resume=True))
                with self.assertRaisesRegex(ValueError, "mismatch"):
                    experiment.run(ROOT, [source], output, judge=False, resume=True, effort="high")
            artifact = output / "cases/fixture/upstream/cleanup.diff"
            artifact.write_text("tampered")
            with self.assertRaisesRegex(ValueError, "artifact changed"):
                experiment.run(ROOT, [source], output, judge=False, resume=True)
            artifact.write_text("")
            row_path = next((output / "cases").rglob("row.json"))
            row = read_json(row_path)
            row["row"]["status"] = "invented"
            write_json(row_path, row)
            with self.assertRaisesRegex(ValueError, "row changed"):
                experiment.run(ROOT, [source], output, judge=False, resume=True)

    def test_build_sources_are_independent_and_upstream_is_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("specs", "dictionary", "vendor"):
                shutil.copytree(ROOT / directory, root / directory)
            shutil.copytree(ROOT / "experiments/claude", root / "experiments/claude")
            before = claude_spec.build(root)
            codex = (root / "specs/codex-changes.md").read_bytes()
            path = root / "specs/claude-base.md"
            path.write_text(path.read_text() + "\nSynthetic instruction.\n")
            with self.assertRaisesRegex(ValueError, "stale"):
                claude_spec.build(root, check=True)
            after = claude_spec.build(root)
            self.assertNotEqual(before["sha256"], after["sha256"])
            self.assertEqual(codex, (root / "specs/codex-changes.md").read_bytes())
            path = root / "vendor/claudish/claudish-to-english.md"
            path.write_text("modified")
            with self.assertRaisesRegex(ValueError, "Pinned"):
                claude_spec.build(root)


if __name__ == "__main__":
    unittest.main()
