"""Apply ordinary unified diffs against supplied source and grade changed comments."""

import re
from pathlib import Path

from .cpp import scan, assert_code_preserved
from .io import safe_path

_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_EXTENSIONS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hh", ".hxx", ".inc"}


def extract(diff, base_dir):
    lines = diff.splitlines(keepends=True)
    pos, results, deleted, seen = 0, [], 0, set()
    while pos < len(lines):
        if lines[pos].startswith(("GIT binary patch", "Binary files", "diff --cc")):
            raise ValueError("Binary and combined diffs are unsupported")
        if not lines[pos].startswith("--- "):
            pos += 1
            continue
        old_name = lines[pos][4:].rstrip("\r\n").split("\t")[0]
        pos += 1
        if pos == len(lines) or not lines[pos].startswith("+++ "):
            raise ValueError("Missing +++ file header")
        new_name = lines[pos][4:].rstrip("\r\n").split("\t")[0]
        pos += 1
        if old_name.startswith("a/"):
            old_name = old_name[2:]
        if new_name.startswith("b/"):
            new_name = new_name[2:]
        if old_name != new_name or old_name == "/dev/null":
            raise ValueError("Use comment-only diffs on existing files; renames are unsupported")
        if old_name.startswith('"') or Path(old_name).suffix not in _EXTENSIONS:
            raise ValueError(f"Unsupported or quoted C/C++ path: {old_name}")
        if old_name in seen:
            raise ValueError(f"Repeated file section: {old_name}")
        seen.add(old_name)
        before = safe_path(base_dir, old_name).read_text(encoding="utf-8")
        source_lines = before.splitlines(keepends=True)
        output, changed, removed_lines = [], set(), set()
        cursor, hunks = 0, 0
        while pos < len(lines):
            if lines[pos].startswith(("diff --git", "--- ")):
                break
            match = _HUNK.match(lines[pos])
            if not match:
                if lines[pos].startswith(("+", "-", " ", "@@", "\\")):
                    raise ValueError("Unexpected content outside diff hunk")
                pos += 1
                continue
            old_start, old_count, new_start, new_count = match.groups()
            old_count = int(old_count) if old_count is not None else 1
            new_count = int(new_count) if new_count is not None else 1
            start = int(old_start) - (1 if old_count else 0)
            if start < cursor or start > len(source_lines):
                raise ValueError("Overlapping or out-of-range hunk")
            output.extend(source_lines[cursor:start])
            cursor = start
            expected_new = int(new_start) - (1 if new_count else 0)
            if len(output) != expected_new:
                raise ValueError("New hunk location does not match reconstructed source")
            pos += 1
            used_old = used_new = 0
            while used_old < old_count or used_new < new_count:
                if pos >= len(lines) or lines[pos][:1] not in (" ", "+", "-"):
                    raise ValueError("Truncated or malformed hunk")
                sign, content = lines[pos][0], lines[pos][1:]
                pos += 1
                if pos < len(lines) and lines[pos].startswith("\\ No newline at end of file"):
                    content = content.rstrip("\r\n")
                    pos += 1
                if sign in (" ", "-"):
                    if cursor >= len(source_lines) or source_lines[cursor] != content:
                        raise ValueError(f"Diff does not match base source: {old_name}:{cursor + 1}")
                    if sign == "-":
                        removed_lines.add(cursor + 1)
                    cursor += 1
                    used_old += 1
                if sign in (" ", "+"):
                    output.append(content)
                    used_new += 1
                    if sign == "+":
                        changed.add(len(output))
                if used_old > old_count or used_new > new_count:
                    raise ValueError("Hunk line counts do not match header")
            hunks += 1
        if not hunks:
            raise ValueError("File section has no hunks")
        output.extend(source_lines[cursor:])
        after = "".join(output)
        old_comments, _ = scan(before)
        comments, _ = scan(after)
        try:
            assert_code_preserved(before, after)
        except ValueError as exc:
            raise ValueError(f"{exc} in {old_name}; supply a comment-only diff") from exc
        deleted += sum(bool(removed_lines.intersection(range(c.line, c.end_line + 1)))
                       for c in old_comments)
        for comment in comments:
            if changed.intersection(range(comment.line, comment.end_line + 1)):
                results.append({
                    "id": f"{old_name}:{comment.line}", "path": old_name,
                    "line": comment.line, "end_line": comment.end_line,
                    "comment": comment.text,
                    "context": "".join(output[max(0, comment.line - 16):comment.end_line + 20]),
                })
    if not seen:
        raise ValueError("No supported unified diff file sections found")
    return {"comments": results, "old_comments_touched": deleted, "files": sorted(seen)}
