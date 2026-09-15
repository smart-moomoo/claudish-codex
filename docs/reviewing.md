# Reviewing changes

Requirements: Python 3.11+ and an authenticated
[Codex CLI](https://learn.chatgpt.com/docs/non-interactive-mode).
Run these commands from this project's directory. No Python dependencies are
needed; `python -m claudish` works directly. Optional: `pip install -e .` adds
the `claudish` command. Use `--root /path/to/claudish-codex` before the subcommand
when invoking it from elsewhere.

Review a mixed-content change with explicit artifact types:

```sh
python -m claudish review-change --input change.json --out runs/change-review
```

This sends the task, before/after artifacts and their context to one fresh
judge using a separately versioned rubric. It never edits source files or
executes the submitted code. See the [input format](change-scope.md#input-format).
The first two criteria are reported as not applicable for text/code; missing
context is unassessed, never a pass. This command makes one model call, unlike
an offline check or the historical commit-shape scorer.

Grade a comment-only diff against the source tree **before** the change:

```sh
python -m claudish grade-diff \
  --diff comments.diff --base-dir /path/to/before-source --out runs/review
```

Every added or changed comment receives a location, six 0–4 grades, evidence,
an explanation, missing facts, and unsupported claims in `grades.json`.
Zero is best; four is a severe problem. The dimensions are Claudishness,
words, structure, simplicity, meaning, and usefulness. A multiline comment is
graded as a whole even when only one line changes. Removed comments are
counted as touched old comments; no replacement text is invented. Attribution
to Codex comes from the caller, since a diff cannot establish authorship.

`--extract-only` saves extracted comments without invoking a model. `--diff -`
reads stdin. Executable token changes and preprocessor changes are rejected.
The grader supports ordinary unified diffs over existing C/C++ files. It
requires matching base content and rejects unsupported paths, binary patches,
combined diffs, renames, line splices and trigraphs. This is a lexical scanner,
not a compiler or a general-language comment parser. It never applies changes
to the supplied source directory.
