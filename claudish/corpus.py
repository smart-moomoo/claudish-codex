"""Fetch and verify a small immutable historical LLVM source corpus."""

import json
from pathlib import Path
import urllib.request

from .cpp import scan
from .io import digest, read_json, safe_path, write_json
from .metrics import measure

LLVM_COMMIT = "d32170dbd5b0d54436537b6b75beaf44324e0c28"
SOURCES = {
    "train": ["llvm/lib/Support/StringRef.cpp", "llvm/lib/Transforms/Utils/Local.cpp"],
    "validation": ["llvm/lib/Analysis/LoopInfo.cpp"],
    "test": ["llvm/lib/Transforms/Utils/BasicBlockUtils.cpp"],
}


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent": "claudish-codex/0.1"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def directory(root, corpus_dir=None):
    return Path(root) / (corpus_dir if corpus_dir is not None else "corpus")


def fetch(root, corpus_dir=None):
    data_dir = directory(root, corpus_dir)
    lock_path = data_dir / "sources.lock.json"
    existing = read_json(lock_path) if lock_path.exists() else None
    source_list = data_dir / "sources.json"
    sources = read_json(source_list) if source_list.exists() else SOURCES
    records = []
    for split, paths in sources.items():
        if split not in ("train", "validation", "test"):
            raise ValueError(f"Invalid source split: {split}")
        for path in paths:
            url = f"https://raw.githubusercontent.com/llvm/llvm-project/{LLVM_COMMIT}/{path}"
            target = safe_path(data_dir / "upstream", path)
            content = target.read_bytes() if target.exists() else download(url)
            expected = next((x["sha256"] for x in existing["files"] if x["path"] == path), None) if existing else None
            if expected and digest(content) != expected:
                raise ValueError(f"LLVM source checksum mismatch: {path}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(content)
            records.append({"path": path, "split": split, "url": url, "sha256": digest(content)})
    license_path = data_dir / "upstream/LICENSE.TXT"
    license_url = f"https://raw.githubusercontent.com/llvm/llvm-project/{LLVM_COMMIT}/llvm/LICENSE.TXT"
    license_bytes = license_path.read_bytes() if license_path.exists() else download(license_url)
    if existing and digest(license_bytes) != existing["license_sha256"]:
        raise ValueError("LLVM license checksum mismatch")
    if not license_path.exists():
        license_path.write_bytes(license_bytes)
    manifest = {
        "repository": "https://github.com/llvm/llvm-project", "tag": "llvmorg-10.0.0",
        "commit": LLVM_COMMIT, "release_date": "2020-03-24",
        "license_url": license_url, "license_sha256": digest(license_bytes),
        "human_reference_basis": "Verbatim comments upstreamed by March 2020, before modern code assistants. Historical provenance, not an individual authorship attestation.",
        "files": records,
    }
    if existing and manifest != existing:
        raise ValueError("Source lock differs; explicitly review the corpus change")
    write_json(lock_path, manifest)
    return manifest


def candidates(root, corpus_dir=None, min_words=12, max_words=65):
    if not 0 < min_words <= max_words:
        raise ValueError("Use positive ordered word-count bounds")
    data_dir = directory(root, corpus_dir)
    lock = read_json(data_dir / "sources.lock.json")
    result = []
    for record in lock["files"]:
        source = safe_path(data_dir / "upstream", record["path"]).read_text()
        comments, _ = scan(source)
        for c in comments:
            metrics = measure(c.text)
            if min_words <= metrics["word_count"] <= max_words and c.line > 20 and not c.text.startswith(("===", "---")):
                result.append({"path": record["path"], "split": record["split"],
                               "line": c.line, "end_line": c.end_line, "text": c.text,
                               "words": metrics["word_count"], "sentences": metrics["sentence_count"]})
    return result


def cases(root, split=None, corpus_dir=None):
    data_dir = directory(root, corpus_dir)
    lock = read_json(data_dir / "sources.lock.json")
    if digest((data_dir / "upstream/LICENSE.TXT").read_bytes()) != lock["license_sha256"]:
        raise ValueError("LLVM license checksum mismatch")
    records = {x["path"]: x for x in lock["files"]}
    selected = read_json(data_dir / "cases.json")
    selection = read_json(data_dir / "selection.json")
    if [{k: v for k, v in c.items() if k != "reference_sha256"} for c in selected] != selection:
        raise ValueError("Selection differs from frozen cases; review and regenerate the corpus")
    seen = set()
    result = []
    for entry in selected:
        if entry["id"] in seen:
            raise ValueError("Duplicate corpus ID")
        seen.add(entry["id"])
        record = records[entry["path"]]
        if entry["split"] != record["split"]:
            raise ValueError("Corpus split must be assigned by file")
        path = safe_path(data_dir / "upstream", entry["path"])
        source_bytes = path.read_bytes()
        if digest(source_bytes) != record["sha256"]:
            raise ValueError(f"Source checksum mismatch: {path}")
        source = source_bytes.decode()
        comments, _ = scan(source)
        comment = next((c for c in comments if c.line == entry["line"]), None)
        if not comment or digest(comment.raw) != entry["reference_sha256"]:
            raise ValueError(f"Reference comment mismatch: {entry['id']}")
        if "min_reference_words" in entry:
            metrics = measure(comment.text)
            if not entry["min_reference_words"] <= metrics["word_count"] <= entry["max_reference_words"]:
                raise ValueError(f"Reference length outside declared stratum: {entry['id']}")
        if split is not None and entry["split"] != split:
            continue
        start = source.rfind("\n", 0, comment.start) + 1
        indent = source[start:comment.start]
        if indent.strip():
            raise ValueError("Corpus currently requires standalone comments")
        # Only a masked context window reaches the generator. No checkout or reference.
        masked = source[:comment.start] + "// <COMMENT_TO_WRITE>" + source[comment.end:]
        masked_lines = masked.splitlines()
        first = max(0, comment.line - 1 - entry.get("context_before", 15))
        last = min(len(masked_lines), comment.line + entry.get("context_after", 45))
        context = "\n".join(masked_lines[first:last])
        source_lines = source.splitlines()
        for begin, end in entry.get("extra_context_ranges", []):
            if not 1 <= begin <= end <= len(source_lines):
                raise ValueError(f"Invalid extra context range: {entry['id']}")
            if begin <= comment.end_line and end >= comment.line:
                raise ValueError(f"Extra context includes target reference: {entry['id']}")
            context += f"\n\n// Additional source context, lines {begin}-{end}:\n"
            context += "\n".join(source_lines[begin - 1:end])
        reference_lines = comment.text.splitlines()
        normalized_context = " ".join(context.split())
        if any(len(line.strip()) > 30 and " ".join(line.split()) in normalized_context for line in reference_lines):
            raise ValueError(f"Reference leakage in context: {entry['id']}")
        result.append({**entry, "reference": comment.text, "raw_reference": comment.raw,
                       "context": context, "indent": indent, "source": source,
                       "start": comment.start, "end": comment.end,
                       "source_url": f"https://github.com/llvm/llvm-project/blob/{lock['commit']}/{entry['path']}#L{comment.line}"})
    if not result:
        raise ValueError(f"No corpus cases for split {split}")
    return result


def prepare(root, corpus_dir=None):
    data_dir = directory(root, corpus_dir)
    lock = fetch(root, corpus_dir)
    frozen = []
    for entry in read_json(data_dir / "selection.json"):
        source = safe_path(data_dir / "upstream", entry["path"]).read_text()
        comments, _ = scan(source)
        comment = next(c for c in comments if c.line == entry["line"])
        frozen.append({**entry, "reference_sha256": digest(comment.raw)})
    target = data_dir / "cases.json"
    if target.exists() and read_json(target) != frozen:
        raise ValueError("Frozen cases differ from selection. Review the change before replacing cases.json.")
    write_json(target, frozen)
    cases(root, corpus_dir=corpus_dir)
    return {"cases": len(frozen), "source_commit": lock["commit"]}
