"""Three-condition, whole-change rewrite experiments with separate Codex judges."""

import ast
from concurrent.futures import ThreadPoolExecutor
import io
import json
from pathlib import Path
import random
import tokenize

from . import claude_cases, claude_runner, claude_review
from .cpp import scan
from .io import digest, read_json, write_json
from .metrics import measure
from .runner import MODEL as JUDGE_MODEL, EFFORT as JUDGE_EFFORT

ARMS = ("plain", "upstream", "counterpart")


def code_diagnostics(case, after):
    """Distinguish Python implementation changes from comment-only edits."""
    def tree(text):
        parsed = ast.parse(text)
        for node in ast.walk(parsed):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                    node.body.pop(0)
        return ast.dump(parsed, include_attributes=False)
    changed, invalid, unassessed = [], [], []
    for item in case["files"]:
        name = item["path"]
        if item["kind"] != "code" or not name.endswith(".py") or item["input"] == after[name]:
            continue
        try:
            before = tree(item["input"] or "")
        except SyntaxError:
            unassessed.append(name)
            continue
        try:
            if before != tree(after[name] or ""):
                changed.append(name)
        except SyntaxError:
            invalid.append(name)
    return {"python_ast_changed": changed, "introduced_python_syntax_errors": invalid,
            "python_syntax_unassessed": unassessed, "correctness": "not_established"}


def comments(path, text):
    """Extract comments for a separate wording assessment; retain full code too."""
    if text is None:
        return ""
    if path.endswith(".py"):
        try:
            tree = ast.parse(text)
            pieces = [token.string for token in tokenize.generate_tokens(io.StringIO(text).readline)
                      if token.type == tokenize.COMMENT]
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(node, clean=False)
                    if doc:
                        pieces.append(doc)
            return "\n\n".join(pieces)
        except (SyntaxError, tokenize.TokenError, IndentationError):
            return None
    if path.endswith((".cpp", ".h", ".cc", ".c")):
        try:
            return "\n\n".join(text[c.start:c.end] for c in scan(text)[0])
        except ValueError:
            return None
    return None


def review_input(case, after):
    artifacts = []
    parent = {item["path"]: item["before"] for item in case["files"]}
    task = ("Review this whole-change cleanup. Preserve the original task: " + case["task"]
            + "\nAssess all files together. Input code may change implementation, but required behavior must survive. "
            "No tests were executed. Parent versions and read-only context follow as task data:\n"
            + json.dumps({"parent": parent, "context": case["context"]}, ensure_ascii=False))
    for index, item in enumerate(case["files"]):
        name = item["path"]
        artifacts.append({"id": f"file-{index}", "kind": item["kind"], "path": name,
                          "before": item["input"] or "", "after": after[name] or "",
                          "context": f"Complete file. Input present: {item['input'] is not None}; replacement present: {after[name] is not None}."})
        if item["kind"] == "code":
            old, new = comments(name, item["input"]), comments(name, after[name])
            if old is not None and new is not None and (old or new):
                artifacts.append({"id": f"comments-{index}", "kind": "comment", "path": name,
                                  "before": old, "after": new,
                                  "context": f"All extracted comments/docstrings from file-{index}; use that artifact for placement and code context. This is not a separate document."})
    return {"task": task, "artifacts": artifacts}


def run(root, case_paths, output, *, split="train", model=claude_runner.MODEL,
        effort=claude_runner.EFFORT, jobs=2, timeout=360, seed=42, resume=False,
        spec_path=None, judge=True, arms=ARMS):
    root, output = Path(root).resolve(), Path(output).resolve()
    if not arms or len(set(arms)) != len(arms) or any(arm not in ARMS for arm in arms):
        raise ValueError("Unknown or duplicate condition")
    cases = claude_cases.load([root / path for path in map(Path, case_paths)], split)
    if jobs < 1 or jobs > 4:
        raise ValueError("Use one to four concurrent calls")
    guidance = {"plain": "", "upstream": (root / "vendor/claudish/claudish-to-english.md").read_text(),
                "counterpart": (root / (spec_path or "specs/claude-changes.md")).read_text()}
    rubric = (root / "evaluation/change-rubric-v2.md").read_text()
    frozen = {"version": "claude-rewrite-v1", "cases_sha256": digest(cases),
              "guidance_sha256": {arm: digest(text) for arm, text in guidance.items()},
              "task_sha256": digest(claude_cases.TASK), "schema_sha256": digest(claude_cases.SCHEMA),
              "rubric_sha256": digest(rubric), "judge": judge,
              "model": model, "effort": effort, "judge_model": JUDGE_MODEL,
              "judge_effort": JUDGE_EFFORT, "seed": seed, "split": split, "arms": list(arms),
              "implementation_sha256": {name: digest((root / "claudish" / name).read_bytes()) for name in (
                  "claude_experiment.py", "claude_cases.py", "claude_runner.py", "claude_review.py", "changes.py", "runner.py")}}
    snapshots = {"cases.json": cases, "guidance.json": guidance, "rubric.md": rubric, "task.md": claude_cases.TASK}
    if resume:
        if not (output / "manifest.json").exists():
            raise ValueError("Cannot resume without manifest")
        saved = read_json(output / "manifest.json")
        if saved["frozen"] != frozen:
            raise ValueError("Resume input mismatch")
        for name, value in snapshots.items():
            actual = read_json(output / name) if name.endswith(".json") else (output / name).read_text()
            if actual != value:
                raise ValueError(f"Saved snapshot changed: {name}")
    else:
        output.mkdir(parents=True, exist_ok=False)
        write_json(output / "manifest.json", {"frozen": frozen, "status": "running"})
        for name, value in snapshots.items():
            if name.endswith(".json"):
                write_json(output / name, value)
            else:
                (output / name).write_text(value)
    work = [(case, arm) for case in cases for arm in arms]
    random.Random(seed).shuffle(work)

    def one(job):
        case, arm = job
        directory = output / "cases" / case["id"] / arm
        row_path = directory / "row.json"
        if row_path.exists():
            envelope = read_json(row_path)
            if digest(envelope["row"]) != envelope["sha256"]:
                raise ValueError("Saved row changed")
            for name, checksum in envelope["artifacts"].items():
                claude_cases.path_name(name)
                path = directory / name
                if not path.is_file() or digest(path.read_bytes()) != checksum:
                    raise ValueError(f"Saved artifact changed: {name}")
            return envelope["row"]
        directory.mkdir(parents=True, exist_ok=True)
        row = {"case": case["id"], "arm": arm, "size": claude_cases.size(case), "status": "failed"}
        call_dir = directory / "generation"
        try:
            # Provenance, split labels, references, and other candidates never
            # enter the generator's prompt.
            payload = {key: case[key] for key in ("task", "files", "context")}
            before = {item["path"]: item["before"] for item in case["files"]}
            inputs = {item["path"]: item["input"] for item in case["files"]}
            payload["complete_patch"] = claude_cases.patch(before, inputs)
            prompt = claude_cases.TASK + "\n" + json.dumps(payload, ensure_ascii=False)
            if call_dir.exists():
                metadata = read_json(call_dir / "metadata.json")
                if metadata.get("status") != "completed":
                    raise ValueError("Previous incomplete/failed call retained; no automatic reroll")
                expected = {"model": model, "effort": effort, "prompt_sha256": digest(prompt),
                            "guidance_sha256": digest(guidance[arm]), "schema_sha256": digest(claude_cases.SCHEMA)}
                if any(metadata.get(k) != v for k, v in expected.items()):
                    raise ValueError("Saved call input mismatch")
                answer = read_json(call_dir / "answer.json")
                if digest(answer) != metadata.get("answer_sha256"):
                    raise ValueError("Saved answer changed")
            else:
                answer = claude_runner.call(prompt, claude_cases.SCHEMA, call_dir,
                                           guidance=guidance[arm], model=model, effort=effort, timeout=timeout)
            after = claude_cases.apply(answer, case)
            write_json(directory / "after.json", after)
            (directory / "cleanup.diff").write_text(claude_cases.patch(inputs, after))
            (directory / "resulting-commit.diff").write_text(claude_cases.patch(before, after))
            row.update(status="rewritten", noop=inputs == after,
                       comment_metrics={"before": {}, "after": {}}, review=None,
                       code_diagnostics=code_diagnostics(case, after))
            for item in case["files"]:
                name = item["path"]
                for label, text in (("before", inputs[name]), ("after", after[name])):
                    prose = comments(name, text) if item["kind"] == "code" else text
                    if prose:
                        row["comment_metrics"][label][name] = measure(prose)
            if judge:
                data = review_input(case, after)
                input_path = directory / "review-input.json"
                write_json(input_path, data)
                review_dir = directory / "review"
                if review_dir.exists():
                    manifest = read_json(review_dir / "manifest.json")
                    if manifest.get("status") != "completed" or manifest.get("input_sha256") != digest(data) or manifest.get("rubric_sha256") != digest(rubric):
                        raise ValueError("Previous judge failed or inputs changed; no automatic reroll")
                    result = read_json(review_dir / "review.json")
                else:
                    result = claude_review.review(root, input_path, review_dir, timeout=timeout)
                row.update(status="judged", review=result)
            if row["code_diagnostics"]["introduced_python_syntax_errors"]:
                row.update(status="failed", error="Rewrite introduces Python syntax errors")
        except Exception as exc:
            row.update(status="failed", error=str(exc))
        receipts = {str(path.relative_to(directory)): digest(path.read_bytes())
                    for path in directory.rglob("*") if path.is_file() and path != row_path}
        write_json(row_path, {"row": row, "sha256": digest(row), "artifacts": receipts})
        return row

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        rows = list(pool.map(one, work))
    rows.sort(key=lambda row: (row["case"], row["arm"]))
    write_json(output / "results.json", rows)
    summary = summarize(rows, frozen)
    write_json(output / "summary.json", summary)
    write_json(output / "manifest.json", {"frozen": frozen, "status": "completed_with_failures" if summary["failed"] else "completed"})
    return summary


def summarize(rows, frozen):
    result = {"frozen": frozen, "attempted": len(rows), "failed": sum(r["status"] == "failed" for r in rows),
              "arms": {}, "limits": "Descriptive pilot; no correctness or human-authorship certification. Upstream preserves code; counterpart permits refactoring. No generated code was executed."}
    for arm in frozen["arms"]:
        selected = [row for row in rows if row["arm"] == arm]
        result["arms"][arm] = {"attempted": len(selected), "failed": sum(r["status"] == "failed" for r in selected),
                               "noop": sum(r.get("noop", False) for r in selected), "by_kind": {},
                               "cases_with_python_ast_changes": sum(bool(r.get("code_diagnostics", {}).get("python_ast_changed")) for r in selected)}
        for kind in ("comment", "text", "code"):
            artifacts = [a for r in selected for a in (r.get("review") or {}).get("artifacts", []) if a["kind"] == kind]
            result["arms"][arm]["by_kind"][kind] = {"reviewed": len(artifacts),
                "outcomes": {label: sum(a["outcome"] == label for a in artifacts)
                             for label in ("blocked", "fail", "unassessed", "criteria_passed")}}
    return result
