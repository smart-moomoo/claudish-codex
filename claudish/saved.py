"""Validate saved inputs before resuming, and keep failed attempts."""

from pathlib import Path
import uuid

from .io import digest, read_json
from .runner import MODEL, EFFORT


def manifest_for_resume(output, expected, snapshots):
    path = output / "manifest.json"
    if not path.exists():
        raise ValueError("Cannot resume without a saved manifest")
    saved = read_json(path)
    mutable = {"status", "started_at", "jobs", "name"}
    for key, value in expected.items():
        if key not in mutable and saved.get(key) != value:
            raise ValueError(f"Resume input mismatch: {key}")
    for name, text in snapshots.items():
        path = output / name
        if not path.exists() or path.read_text() != text:
            raise ValueError(f"Resume input mismatch: {name}")
    return saved


def completed(call_dir, prompt, schema, *, guidance="", model=MODEL, effort=EFFORT):
    path = call_dir / "metadata.json"
    if not path.exists():
        return None
    metadata = read_json(path)
    expected = {"model": model, "reasoning_effort": effort,
                "prompt_sha256": digest(prompt), "schema_sha256": digest(schema),
                "guidance_sha256": digest(guidance)}
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValueError(f"Saved call input mismatch: {call_dir}: {key}")
    for name, value in (("prompt.txt", prompt), ("guidance.md", guidance)):
        if not (call_dir / name).exists() or (call_dir / name).read_text() != value:
            raise ValueError(f"Saved call input mismatch: {call_dir}: {name}")
    if not (call_dir / "schema.json").exists() or read_json(call_dir / "schema.json") != schema:
        raise ValueError(f"Saved call input mismatch: {call_dir}: schema.json")
    if metadata.get("status") == "completed":
        if not (call_dir / "answer.json").exists():
            raise ValueError(f"Completed call is missing its answer: {call_dir}")
        return read_json(call_dir / "answer.json")
    return None


def archive_attempt(call_dir):
    call_dir = Path(call_dir)
    if call_dir.exists():
        archive = call_dir.parent / "attempts"
        archive.mkdir(exist_ok=True)
        call_dir.rename(archive / f"{call_dir.name}-{uuid.uuid4().hex}")
