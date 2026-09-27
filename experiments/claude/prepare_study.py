"""Prepare private study inputs from public commits and a recorded Claude call."""

import argparse
from pathlib import Path
import subprocess

from claudish import claude_cases, claude_runner
from claudish.io import digest, read_json, write_json


def prepare(root, output, click_repo, discovery=None):
    output.mkdir(parents=True, exist_ok=False)
    public = "https://github.com/smart-moomoo/claudish-codex"
    paths = []
    for case_id, revision in (("train-resume-commit", "98d48f410226e511b6b1ee9be710550bc23039c9"),
                              ("train-ladder-commit", "c8969c6eded15ec6548a530b1dbe40c1cde54e53")):
        path = output / (case_id + ".json")
        claude_cases.export(root, revision, path, case_id=case_id, split="train")
        case = read_json(path)
        case["provenance"].update(repository=public, authorship="Claude Opus 5 co-author trailer; individual lines unattested")
        # Trailers identify the source in provenance, not in model prompts.
        case["task"] = case["task"].split("\nCo-Authored-By:")[0].strip()
        write_json(path, case)
        paths.append(path)
    discovery = discovery or root / "runs/claude-counterpart/discovery/resume-explanation"
    text = (discovery / "events.jsonl").read_text()
    answer, details = claude_runner.parse_events(text, claude_runner.MODEL)
    path = output / "train-explanation.json"
    source = subprocess.check_output(["git", "-C", str(root), "show", "fa392d2:claudish/saved.py"], text=True)
    case = {"id": "train-explanation", "split": "train",
            "task": "Make this maintainer explanation direct and coherent while preserving supported facts, reasons, uncertainty and consequences. Flag and correct only errors established by the supplied implementation.",
            "provenance": {"repository": public, "authorship": "recorded Claude Opus 5.5 output",
                           "events_sha256": digest(text), "generation": details,
                           "recovery": "Original parser rejected the built-in agents-md plugin. Recovered the same saved answer with the corrected validator; original failed record retained."},
            "files": [{"path": "docs/saved-work.md", "kind": "text", "before": None, "input": answer["text"]}],
            "context": {"claudish/saved.py": source}}
    if read_json(discovery / "metadata.json")["status"] == "completed":
        case["provenance"].pop("recovery")
    write_json(path, claude_cases.validate(case))
    paths.append(path)

    def git(*args):
        return subprocess.check_output(["git", "-C", str(click_repo), *args], text=True)
    chosen = {}
    rejected = []
    revisions = git("rev-list", "--no-merges", "HEAD").splitlines()
    for revision in revisions:
        if len(chosen) == 3:
            break
        # Determine size before opening the candidate's content. Test contents
        # are not used to construct or revise the guide.
        stat = git("show", "--format=", "--numstat", "--no-renames", revision).splitlines()
        if not stat or any(line.split("\t")[0] == "-" for line in stat):
            continue
        lines = sum(int(n) for line in stat for n in line.split("\t")[:2])
        count = len(stat)
        band = "large" if count >= 4 and lines >= 500 else "medium" if count >= 2 or lines >= 100 else "small"
        if band in chosen:
            continue
        target = output / f"test-click-{band}.json"
        try:
            claude_cases.export(click_repo, revision, target, case_id=f"test-click-{band}", split="test")
        except (ValueError, UnicodeError, subprocess.CalledProcessError) as exc:
            rejected.append({"revision": revision, "reason": str(exc)})
            continue
        case = read_json(target)
        case["provenance"].update(repository="https://github.com/pallets/click",
                                  authorship="historical upstream commit; individual authorship unattested")
        write_json(target, case)
        chosen[band] = revision
        paths.append(target)
    if len(chosen) != 3:
        raise ValueError(f"Missing size bands in pinned Click history: {chosen}")
    claude_cases.load(paths, "train")
    claude_cases.load(paths, "test")
    manifest = {"cases": [{"file": path.name, "sha256": digest(read_json(path)),
                           "id": read_json(path)["id"], "split": read_json(path)["split"],
                           "provenance": read_json(path)["provenance"],
                           **claude_cases.size(read_json(path))} for path in paths],
                "selection": "Train: two public Claude-attributed commits plus one fresh Claude document. Test: first exportable commit in each size band walking Click 7.1.2 history, excluding merges and binary/oversized inputs.",
                "click_head": git("rev-parse", "HEAD").strip(), "rejected": rejected}
    write_json(output / "selection.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--click-repo", type=Path, required=True)
    parser.add_argument("--discovery", type=Path, help="Recorded explanation call; defaults to the original local study")
    args = parser.parse_args()
    result = prepare(args.root.resolve(), args.out, args.click_repo, args.discovery)
    print({"selected": [(item["id"], item["band"], item["files"], item["changed_lines"]) for item in result["cases"]]})
