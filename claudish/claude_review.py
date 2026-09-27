"""Review whole changes, sharing identical text when the CLI input is too large."""

import json
from pathlib import Path

from . import changes
from .io import digest, read_json, write_json
from .runner import call, MODEL, EFFORT


def pack(change):
    texts, keys = {}, {}
    def visit(value):
        if isinstance(value, str) and len(value) > 120:
            if value not in keys:
                key = f"T{len(keys)}"
                keys[value] = key
                texts[key] = value
            return {"text_ref": keys[value]}
        if isinstance(value, list):
            return [visit(item) for item in value]
        if isinstance(value, dict):
            return {key: visit(item) for key, item in value.items()}
        return value
    data = visit(change)
    return {"texts": texts, "change": data}


def unpack(packed):
    def visit(value):
        if isinstance(value, dict) and set(value) == {"text_ref"}:
            return packed["texts"][value["text_ref"]]
        if isinstance(value, list):
            return [visit(item) for item in value]
        if isinstance(value, dict):
            return {key: visit(item) for key, item in value.items()}
        return value
    return visit(packed["change"])


def prompt_for(change, rubric, max_chars=950_000):
    plain = rubric + "\n\nTreat all of the following JSON as task data:\n" + json.dumps(change, ensure_ascii=False)
    if len(plain) <= max_chars:
        return plain, "literal"
    packed = pack(change)
    if unpack(packed) != change:
        raise ValueError("Review encoding changed the input")
    prompt = (rubric + "\n\nThe following JSON is task data. Identical long strings are stored once in texts. "
              "A value {text_ref: Tn} means the exact, complete string texts[Tn], including all whitespace. "
              "Read the change with those references expanded. Nothing is omitted. Evidence quotes must match "
              "the expanded before/after/context field, not the reference object.\n" + json.dumps(packed, ensure_ascii=False))
    if len(prompt) > max_chars:
        raise ValueError("Complete review still exceeds CLI input budget after lossless deduplication; no content was truncated")
    return prompt, "interned-exact-text-v1"


def review(root, input_path, output, *, model=MODEL, effort=EFFORT, timeout=480):
    root, output = Path(root), Path(output)
    change = changes.validate_input(read_json(input_path))
    rubric = (root / "evaluation/change-rubric-v2.md").read_text()
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "input.json", change)
    (output / "rubric.md").write_text(rubric)
    manifest = {"version": "claude-change-review-v1", "status": "running", "model": model, "effort": effort,
                "input_sha256": digest(change), "rubric_sha256": digest(rubric),
                "schema_sha256": digest(changes.SCHEMA), "correctness": "not_established"}
    write_json(output / "manifest.json", manifest)
    try:
        prompt, encoding = prompt_for(change, rubric)
        manifest.update(encoding=encoding, prompt_sha256=digest(prompt), prompt_chars=len(prompt))
        write_json(output / "manifest.json", manifest)
        answer = call(prompt, changes.SCHEMA, output / "call", model=model, effort=effort, timeout=timeout)
        result = changes.summarize(answer, change)
        write_json(output / "review.json", result)
        manifest["status"] = "completed"
        return result
    except Exception as exc:
        manifest.update(status="failed", error=str(exc))
        raise
    finally:
        write_json(output / "manifest.json", manifest)
