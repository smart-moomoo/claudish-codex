"""Rebuild corrected public aggregates from private, already completed runs.

Run with python -m experiments.ladder.publish from the project root.
Makes no model calls. Raw answers, comments and explanations stay local.
"""

from pathlib import Path
import shutil
from statistics import median

from claudish import experiment, filelevel, tiers
from claudish.io import digest, read_json, write_json

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "experiments/ladder"


def preserve(path, destination):
    if path.exists() and not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)


def main():
    for name in ("commits.json", "file-sets.json", "tiers-unseen.json"):
        preserve(PUBLIC / name, PUBLIC / "superseded-v1" / name)
    runs = [(split, ROOT / "experiments/scaled" / split) for split in ("validation", "test")]
    summaries, file_sets = {}, {}
    for split, path in runs:
        preserve(path / "tiers.json", path / "tiers-v1.json")
        summaries[split] = tiers.score_run(path, experiment.reload_corpus)
        saved = read_json(path / filelevel.JUDGMENTS)
        file_sets[split] = {
            "summary": saved["summary"], "inputs": saved["inputs"],
            "requested_files": saved["requested_files"],
            "invalid_judgments": saved["invalid_judgments"],
            "files": [{"path": item["path"], "arm": item["arm"], "comments": item["comments"],
                       **{key: item["optimal"][key] for key in ("passed", *filelevel.DEFICITS)}}
                      for item in saved["files"]]}
    write_json(PUBLIC / "tiers-unseen.json", {"runs": summaries, "pooled": tiers.combine(runs),
               "file_judge_version": 2,
               "note": "Fourth-rung coverage excludes invalid file judgments; missing grades are not failures. "
                       "Meaning remains a separate score, not a gate."})
    write_json(PUBLIC / "file-sets.json", {
        "version": 2, "rubric": "evaluation/file-rubric.md", "runs": file_sets,
        "note": "17 fresh calls with corrected code context; 1 invalid response preserved and excluded, "
                "not rerolled. The prior leaked-context series is superseded."})
    path = PUBLIC / "commits-01-rescored"
    manifest = read_json(path / "manifest.json")
    rows = read_json(path / "results.json")
    cases = []
    for row in rows:
        item = {key: row[key] for key in ("id", "url", "arm", "applied", "invalid")}
        if row["applied"]:
            comparison = row["comparison"]
            item.update(region_overlap=comparison["region_overlap"],
                        changed_lines=comparison["invasive"]["changed_lines"],
                        reference_changed_lines=comparison["invasive"]["reference_changed_lines"],
                        invasive_passed=comparison["invasive"]["passed"],
                        optimal_passed=comparison["optimal"]["passed"])
        cases.append(item)
    write_json(PUBLIC / "commits.json", {
        "run": path.name, "source_run": "commits-01", "scoring_version": 2,
        **{key: manifest[key] for key in ("split", "model", "effort", "arms", "task_sha256",
                                         "commits_sha256", "overlap_threshold")},
        "source_manifest_sha256": manifest["source_manifest_sha256"],
        "results_sha256": digest(rows), "new_model_calls": 0,
        "summary": read_json(path / "summary.json"), "cases": cases,
        "median_changed_lines": median(item["changed_lines"] for item in cases if item["applied"]),
        "median_reference_changed_lines": median(item["reference_changed_lines"] for item in cases),
        "note": "Shape only. Nothing was compiled or tested. Original and final sources use the same "
                "diff algorithm; replacement anchors are not counted as edits."})
    print("Published corrected file, ladder and commit aggregates; raw artifacts remain local.")


if __name__ == "__main__":
    main()
