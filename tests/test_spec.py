"""Contracts for building the spec from reviewed dictionary entries."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from claudish.spec import build, validate

ROOT = Path(__file__).resolve().parents[1]


def entry(**overrides):
    base = {"id": "sample-rule", "dimension": "words", "guidance": "Say the thing plainly.",
            "before": "Utilize the load-bearing abstraction.", "after": "Use the buffer.",
            "exceptions": ["Keep a real compiler term."], "signals": ["load-bearing"],
            "evidence": ["experiments/ITERATIONS.md#round-02-result"],
            "example_origin": "synthetic"}
    return {**base, **overrides}


class EvidenceLinks(unittest.TestCase):
    def test_a_link_into_a_private_run_directory_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "committed file"):
            validate([entry(evidence=["experiments/round-01/report.md#local-switch"])], ROOT)

    def test_a_committed_file_and_a_url_are_accepted(self):
        validate([entry()], ROOT)
        validate([entry(evidence=["https://github.com/llvm/llvm-project/blob/x/y.cpp#L10"])], ROOT)

    def test_an_unanchored_link_is_still_rejected(self):
        with self.assertRaisesRegex(ValueError, "source or an experiment artifact"):
            validate([entry(evidence=["runs/local/report.md"])], ROOT)

    def test_the_shipped_dictionary_links_all_resolve(self):
        entries = json.loads((ROOT / "dictionary/entries.json").read_text())
        validate(entries, ROOT)


class ProvenanceStamp(unittest.TestCase):
    def copy_project(self, root):
        for name in ("specs", "dictionary"):
            shutil.copytree(ROOT / name, Path(root) / name)
        return Path(root)

    def test_editing_a_reviewer_note_leaves_the_spec_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_project(directory)
            before = build(root)
            path = root / "dictionary/entries.json"
            entries = json.loads(path.read_text())
            entries[-1]["evidence"] = ["https://example.com/a-different-writeup"]
            entries[-1]["signals"] = ["a different hint"]
            path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n")
            after = build(root)
        # Reviewer notes do not change generated guidance or its provenance.
        self.assertEqual(before["sha256"], after["sha256"])
        self.assertEqual(before["input_sha256"], after["input_sha256"])
        self.assertEqual(before["changes_sha256"], after["changes_sha256"])

    def test_editing_guidance_does_change_the_spec(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_project(directory)
            before = build(root)
            path = root / "dictionary/entries.json"
            entries = json.loads(path.read_text())
            entries[-1]["guidance"] = "Completely different guidance."
            path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n")
            after = build(root)
        self.assertNotEqual(before["sha256"], after["sha256"])
        self.assertNotEqual(before["body_sha256"], after["body_sha256"])

    def test_archived_body_matches_the_frozen_scaled_candidate(self):
        record = json.loads((ROOT / "experiments/scaled/frozen-candidate.json").read_text())
        text = (ROOT / "specs/archive/scaled-comments.md").read_text()
        from claudish.io import digest
        self.assertEqual(digest(text.split("\n", 1)[1]), record["spec_body_sha256"])
        self.assertNotEqual(text, (ROOT / "specs/codex-comments.md").read_text())

    def test_shared_prose_updates_both_guides_without_touching_the_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_project(directory)
            archive = {p.name: p.read_bytes() for p in (root / "specs/archive").iterdir()}
            before = build(root)
            path = root / "specs/prose-base.md"
            path.write_text(path.read_text() + "\nSynthetic shared instruction.\n")
            with self.assertRaisesRegex(ValueError, "stale"):
                build(root, check=True)
            after = build(root)
            self.assertNotEqual(before["sha256"], after["sha256"])
            self.assertNotEqual(before["changes_sha256"], after["changes_sha256"])
            prose = path.read_text().strip()
            for name in ("codex-comments.md", "codex-changes.md"):
                self.assertEqual((root / "specs" / name).read_text().count(prose), 1)
            self.assertEqual(archive, {p.name: p.read_bytes() for p in (root / "specs/archive").iterdir()})
            build(root, check=True)


if __name__ == "__main__":
    unittest.main()
