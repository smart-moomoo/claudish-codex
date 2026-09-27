"""Freeze study inputs and publish aggregates without exporting raw model text."""

import argparse
from datetime import datetime, timezone
from pathlib import Path

from claudish import claude_experiment
from claudish.io import digest, read_json, write_json


SOURCES = ("specs/claude-changes.md", "specs/claude-base.md", "dictionary/claude.json",
           "vendor/claudish/claudish-to-english.md", "vendor/claudish/source.json",
           "evaluation/change-rubric-v2.md", "claudish/claude_runner.py",
           "claudish/claude_cases.py", "claudish/claude_experiment.py",
           "claudish/changes.py", "claudish/runner.py", "claudish/claude_spec.py",
           "claudish/cli.py", "experiments/claude/PROTOCOL.md")


def freeze(root, cases_dir, target):
    if target.exists():
        raise FileExistsError(target)
    selection = read_json(cases_dir / "selection.json")
    for record in selection["cases"]:
        if digest(read_json(cases_dir / record["file"])) != record["sha256"]:
            raise ValueError("Selected case changed")
        # Public provenance needs source revisions and hashes, not session IDs.
        record["provenance"].pop("generation", None)
    result = {"frozen_at": datetime.now(timezone.utc).isoformat(), "selection": selection,
              "sources": {name: digest((root / name).read_bytes()) for name in SOURCES},
              "model": "claude-opus-5-5", "effort": "medium", "judge": "gpt-5.6-sol",
              "judge_effort": "medium", "heldout_policy": "No tuning after this freeze; previously exposed LLVM tests are excluded."}
    write_json(target, result)
    return result


def outcome(row):
    if row["status"] == "failed":
        return "failed_call_or_validation"
    artifacts = (row.get("review") or {}).get("artifacts", [])
    for label in ("blocked", "fail", "unassessed"):
        if any(a["outcome"] == label for a in artifacts):
            return label
    return "criteria_passed" if artifacts else "not_judged"


def publish(root, runs, freeze_path, target):
    frozen = read_json(freeze_path)
    recovery_dir = root / "runs/claude-counterpart/large-review-recovery"
    recovery = read_json(recovery_dir / "manifest.json")
    if recovery["original_freeze_sha256"] != digest(frozen):
        raise ValueError("Recovery belongs to a different freeze")
    if recovery["source_sha256"] != digest((root / "claudish/claude_review.py").read_bytes()):
        raise ValueError("Recovery adapter changed since its recorded review")
    amendment = read_json(root / "experiments/claude/transport-amendment.json")
    if amendment["original_freeze_sha256"] != digest(frozen):
        raise ValueError("Transport amendment belongs to a different freeze")
    for name, checksum in amendment["added_sources"].items():
        if digest((root / name).read_bytes()) != checksum:
            raise ValueError(f"Added transport source changed: {name}")
    transport_changes = {}
    for name, checksum in frozen["sources"].items():
        current = digest((root / name).read_bytes())
        if current != checksum:
            recorded = amendment["changed_sources"].get(name)
            if recorded != {"before": checksum, "after": current}:
                raise ValueError(f"Source changed after freeze: {name}")
            transport_changes[name] = {"before": checksum, "after": current}
    recovery_groups = []
    for group in recovery["groups"]:
        reviewed = group.get("review", {}).get("artifacts", [])
        recovery_groups.append({"input_sha256": group["input_sha256"], "conditions": group["conditions"],
            "status": group["status"], "error": group.get("error", "").replace(str(root), "<project>") or None,
            "review_sha256": digest(group["review"]) if "review" in group else None,
            "outcomes": {label: sum(a["outcome"] == label for a in reviewed)
                         for label in ("blocked", "fail", "unassessed", "criteria_passed")}})
    result = {"freeze_sha256": digest(frozen), "post_freeze_transport_changes": transport_changes,
              "large_review_recovery": {"scope": recovery["scope"], "source_sha256": recovery["source_sha256"],
                                        "groups": recovery_groups}, "runs": {}, "limits": [
        "Small descriptive study; no statistical or correctness certification.",
        "Human-era Click commits are preservation controls, not verified Claude outputs.",
        "Code refactoring is allowed by the counterpart but not by the upstream prose spec.",
        "Judge blockers can concern inherited defects; they are not all rewrite regressions.",
        "Raw answers and invalid reviews remain local; failed attempts are included.",
        "The large-case transport failure informed an implementation change; these exposed test cases are retired as untouched holdouts."]}
    for label, directory in runs.items():
        summary = read_json(directory / "summary.json")
        manifest = read_json(directory / "manifest.json")["frozen"]
        if manifest["rubric_sha256"] != frozen["sources"]["evaluation/change-rubric-v2.md"]:
            raise ValueError("Judge rubric changed across rounds")
        if manifest["split"] == "test" and manifest["guidance_sha256"]["counterpart"] != frozen["sources"]["specs/claude-changes.md"]:
            raise ValueError("Heldout run did not use frozen guide")
        cases = {case["id"]: case for case in read_json(directory / "cases.json")}
        details = []
        for row in read_json(directory / "results.json"):
            case = cases[row["case"]]
            location = directory / "cases" / row["case"] / row["arm"]
            diagnostics = None
            if (location / "after.json").exists():
                diagnostics = claude_experiment.code_diagnostics(case, read_json(location / "after.json"))
            reviewed = (row.get("review") or {}).get("artifacts", [])
            details.append({"case": row["case"], "arm": row["arm"], "size": row["size"],
                            "outcome": outcome(row), "error": row.get("error", "").replace(str(root), "<project>") or None, "noop": row.get("noop"),
                            "python_ast_changed_files": len((diagnostics or {}).get("python_ast_changed", [])),
                            "python_syntax_errors": len((diagnostics or {}).get("introduced_python_syntax_errors", [])),
                            "blocked_artifacts": sum(a["outcome"] == "blocked" for a in reviewed),
                            "prose_words_before": sum(m["word_count"] for m in row.get("comment_metrics", {}).get("before", {}).values()),
                            "prose_words_after": sum(m["word_count"] for m in row.get("comment_metrics", {}).get("after", {}).values())})
        calls = []
        for path in directory.rglob("metadata.json"):
            data = read_json(path)
            calls.append({"provider": data.get("provider", "codex-cli"), "model": data["model"],
                          "status": data["status"], "elapsed_seconds": data.get("elapsed_seconds"),
                          "cost_usd_estimate": data.get("cost_usd"),
                          "usage": data.get("usage"), "cli_version": data.get("cli_version", data.get("codex_version"))})
        result["runs"][label] = {"summary": summary, "cases": details, "calls": calls,
                                 "raw_results_sha256": digest(read_json(directory / "results.json"))}
    write_json(target, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "publish"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--cases", type=Path, default=Path("runs/claude-counterpart/cases"))
    parser.add_argument("--freeze", type=Path, default=Path("experiments/claude/frozen.json"))
    parser.add_argument("--out", type=Path, default=Path("experiments/claude/results.json"))
    args = parser.parse_args()
    if args.action == "freeze":
        result = freeze(args.root, args.cases, args.freeze)
        print({"frozen": str(args.freeze), "sha256": digest(result)})
    else:
        base = args.root / "runs/claude-counterpart"
        result = publish(args.root, {name: base / name for name in ("train-r1", "train-r2", "heldout")}, args.freeze, args.out)
        print({name: [(c["case"], c["arm"], c["outcome"]) for c in data["cases"]]
               for name, data in result["runs"].items()})
