"""Review saved large outputs after a transport failure, without regenerating them."""

from datetime import datetime, timezone
from pathlib import Path

from claudish import claude_review
from claudish.io import digest, read_json, write_json


def recover(root, run, output):
    output.mkdir(parents=True, exist_ok=False)
    groups = {}
    for row in read_json(run / "results.json"):
        if row["size"]["band"] != "large":
            continue
        path = run / "cases" / row["case"] / row["arm"] / "review-input.json"
        data = read_json(path)
        key = digest(data)
        groups.setdefault(key, {"input": path, "conditions": []})["conditions"].append({"case": row["case"], "arm": row["arm"]})
    frozen = read_json(root / "experiments/claude/frozen.json")
    for name in ("specs/claude-changes.md", "dictionary/claude.json", "evaluation/change-rubric-v2.md"):
        if digest((root / name).read_bytes()) != frozen["sources"][name]:
            raise ValueError("Guidance or rubric changed; this is not transport-only recovery")
    record = {"frozen_at": datetime.now(timezone.utc).isoformat(), "original_freeze_sha256": digest(frozen),
              "reason": "Original full review exceeded Codex CLI's 1048576-character limit. Intern identical whole strings without omitting content.",
              "source_sha256": digest((root / "claudish/claude_review.py").read_bytes()),
              "rubric_sha256": frozen["sources"]["evaluation/change-rubric-v2.md"],
              "scope": "Post-hoc transport recovery; not an untouched heldout test. Identical expanded inputs share one fresh judgment, not independent ratings.",
              "groups": []}
    write_json(output / "manifest.json", record)
    for index, (checksum, group) in enumerate(groups.items()):
        entry = {"input_sha256": checksum, "conditions": group["conditions"]}
        try:
            result = claude_review.review(root, group["input"], output / f"review-{index}", timeout=600)
            entry.update(status="completed", review=result)
        except Exception as exc:
            entry.update(status="failed", error=str(exc))
        record["groups"].append(entry)
        write_json(output / "manifest.json", record)
    return record


if __name__ == "__main__":
    root = Path.cwd()
    result = recover(root, root / "runs/claude-counterpart/heldout", root / "runs/claude-counterpart/large-review-recovery")
    print({"unique_inputs": len(result["groups"]), "statuses": [g["status"] for g in result["groups"]]})
