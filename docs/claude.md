# De-Claude a whole change

Use [the Claude guide](../specs/claude-changes.md) to revise prose, comments and
code while preserving meaning and required behavior. It starts from a pinned
[upstream Claudish spec](../vendor/claudish/claudish-to-english.md), with a separate
extension for cross-file organization and code refactoring. It does not load
the Codex guide or dictionary. Copy the guide and upstream MIT license into
your project, and ask Claude to follow the guide for the selected input.

The tools use Python 3.11+ and the standard library. Model work requires the
local Claude CLI and, for reviews, the Codex CLI. The tested Claude configuration
is `claude-opus-5-5`, medium effort. Judges use `gpt-5.6-sol`, medium effort.
An unavailable model fails the call; there is no fallback model.

## Rewrite a commit

From this project's root, export the entire commit, including all changed files:

```sh
python -m claudish export-claude-commit --repo /path/to/project --revision HEAD \
  --id my-change --out runs/my-change.json --context path/to/caller.py
python -m claudish claude-rewrite --case runs/my-change.json --out runs/my-rewrite --judge
```

Use `--task` to supply the original requirements when the commit message is
insufficient. Repeat `--context` for unchanged callers, tests or documents
needed to understand the change. Context is read-only; changed files are
editable. The exporter reads Git objects and does not change the checkout.
Raw source is sent to the selected model services when you run a rewrite or
review. Inspect the input first and use only material you may send there.

The default 600,000-byte case limit rejects an oversized commit rather than
cropping it. Increase `--max-bytes` explicitly when the model context and budget
permit. The exporter accepts one-parent commits with UTF-8 regular text files;
binary files, symlinks and submodules are rejected. Renames are represented as
deletion plus addition. Unsupported metadata-only changes must be handled
outside this text-rewrite workflow.

The output contains `cleanup.diff` against the supplied input and
`resulting-commit.diff` against its parent, plus complete replacement snapshots.
These are review artifacts, not automatically applied patches. Generated code
is never executed. Review behavior, file metadata and application in your own
project before accepting a change. A no-op is valid when the input needs none.

## Supply a document or comment block

A case is JSON with `id`, `split`, `task`, `provenance`, `files` and `context`.
Each file has `path`, `kind` (`text`, `comment` or `code`), `before` (parent
version), and `input` (the version to improve). Use null for an absent file,
not an empty string. `context` maps read-only paths to full text. For a document
without a parent, use null for `before` and the complete document for `input`.
Record the actual source in `provenance`; never infer authorship from wording.

The model returns exact, nonoverlapping replacements anchored in the input.
Invalid anchors, edits outside the supplied paths and malformed responses fail
validation. Nothing writes into the input repository. Python and C/C++ comments
receive separate wording scores with their full source available to the judge;
other code languages receive code review without extracted comment scores.

## Compare the three conditions

```sh
python -m claudish claude-ablate \
  --case runs/train-case.json --case runs/test-case.json \
  --split train --out runs/claude-training --jobs 2
```

Each input receives a plain cleanup request, the unmodified upstream spec,
and the counterpart guide. All share the same task and response contract.
Upstream tells the model to preserve code verbatim; the counterpart explicitly
permits behavior-preserving refactoring. Report that scope difference when
interpreting results. Do not call a code-refactoring difference a pure prose
style improvement.

Every generation and judgment starts fresh. The Claude runner uses an empty
working directory and temporary config containing credentials only, safe mode,
disabled skills/tools, an empty MCP configuration and no session persistence.
It rejects unexpected tools, user plugins or a different reported model.
The CLI's built-in AGENTS loader is allowed only with no ancestor instruction
files. Managed platform policies still apply; this is not a claim that the
provider's system prompt or infrastructure is absent.

Codex judges see anonymous before/after artifacts, complete parent files and
context, but no condition label, evolving dictionary or previous answer. The
fixed rubric is `evaluation/change-rubric-v2.md`. Cleanliness/effectiveness
apply only to comments; invasiveness/optimality apply to every artifact kind.
Missing context remains unassessed. Reviews do not establish correctness.

For large reviews, the transport stores identical long strings once and uses
references to that complete text. It checks that expanding the references
reconstructs the original input exactly. It never crops files or hunks to fit.
An input that still exceeds the CLI character budget fails before a model call.
The original study exposed this limit; its post-hoc recovery is reported
separately, and the affected test corpus is retired as an untouched holdout.

## Resume and inspect

Repeat the same command with `--resume` and identical inputs to reuse saved
work. Completed rows, including failures, are reused. Successful calls saved
before an interruption can be recovered. Failed/incomplete calls are retained,
not automatically retried or selectively rerolled. A new experiment directory
is a new attempt and must not replace an unfavorable result in a report.

Each run snapshots its cases, guides, task and rubric with hashes. Call folders
retain prompts, schemas, events, metadata and answers. Hash checks refuse stale
inputs, changed runner implementations, and modified saved artifacts. Python
AST diagnostics distinguish executable changes from comment/docstring edits;
an introduced parse error fails the case. They do not establish behavior or
require the implementation to remain unchanged. `summary.json` reports every attempted condition and separates results
by artifact kind; `results.json` retains per-case reviews and descriptive text
metrics. Inspect whole contrasts, not only a pass count.

## Change the guide

Edit `specs/claude-base.md` and `dictionary/claude.json`, then run:

```sh
python -m claudish build-claude-spec
```

The dictionary selects pinned upstream examples and adds contextual rules with
synthetic before/after pairs, exceptions and public evidence. Accepted entries
change the generated guide; search terms are not banned words. Keep imported
upstream files immutable. Updating upstream requires a deliberate revision/hash
change and a new comparison baseline. The Codex sources remain independent.

See the [study protocol](../experiments/claude/PROTOCOL.md) and
[results](../experiments/claude/README.md). Tune only on training data; freeze
choices before evaluating fresh file-disjoint holdouts. Report failures and
regressions. Raw runs and downloaded repositories remain under ignored `runs/`.
