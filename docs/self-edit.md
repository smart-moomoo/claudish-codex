# Applying the spec to this repository

The sections below record the initial prose-only pass. The later
[general-change pass](#general-change-pass) also refactors executable code.

This is an editorial cleanup, not an evaluation of the spec's effectiveness.
It starts from commit `47b6fc9d3345ea37c4b566a474999c488f2d1a18`.

The editing guide was frozen before any changes:

- `specs/codex-comments.md` SHA-256:
  `f271a6340124c2b3b748f0ca1c1d164c8286ebfc66a8da3b4337a6c6934d7bb9`
- `dictionary/entries.json` SHA-256:
  `67900695ca390df0b9923222281a6ed1b2f952b42234dd5a49c525cde077698a`

Four fresh, isolated `codex exec` sessions used `gpt-5.6-sol` with medium
reasoning. Each received the frozen guide, original files as context, and a
list of editable prose fragments. The sessions proposed 28 replacements,
which were reviewed before applying them. Some proposals were revised to
avoid unsupported claims. Raw proposals and call records stay local under
`runs/self-edit/`.

## Scope

The pass considered explanatory comments and docstrings in tracked Python
files, plus narrative paragraphs in the main README, contribution guide,
dictionary README, and corpus READMEs. It prioritized passages of at least
25 words. Clear passages and shorter comments were left alone. Eleven existing
files changed.

The spec and dictionary were not edited. Neither were prompts, rubrics,
fixtures, commands, contribution requirements, licenses, historical protocols,
experiment reports, aggregate results, or upstream reference text. The main
README's summaries retain their numerical results and qualifications.

## Examples

In [experiment.py](../claudish/experiment.py), the resume explanation now
describes which calls are repeated instead of making a claim about cost.

Before:

> A stopped run keeps everything it already paid for. Only the calls that
> never finished are made again, so stopping a long run is cheap.

After:

> Only calls that never finished are made again; completed calls from the
> stopped run are preserved and reused.

In [tiers.py](../claudish/tiers.py), the identifier heuristic no longer claims
to distinguish code names from ordinary prose without error.

Before:

> Whether a token can only be a code name, never ordinary prose.

After:

> Whether a token has the code-name forms recognized by this metric.

In the [500-comment corpus README](../corpus/scaled-500/README.md), the scope
limitation replaces a rhetorical aside.

Before:

> Earlier corpora drew only on Analysis, Transforms, CodeGen and Support. This
> one spans sixteen subsystems, which is the point: the earlier studies could not
> speak to LLVM beyond the handful of passes they sampled.

After:

> Earlier corpora drew only on Analysis, Transforms, CodeGen and Support. This
> corpus spans sixteen subsystems; the earlier studies covered only the handful
> of passes they sampled and could not support conclusions about LLVM beyond
> them.

## Preservation checks

Python ASTs were compared before and after, allowing only docstring changes.
All other string literals, including prompts and fixtures, are unchanged.
Markdown checks compared fenced examples, inline code, link targets, headings,
and numbers. The frozen spec and dictionary hashes still match. Review also
checked that qualifications and requirements were retained. No smoke tests or
new LLVM experiments were run.

The spec's own wording remains outside this pass. Any proposed revision to it
needs a separate change and the existing contribution workflow.

## General-change pass

This pass brings main commit `7870906316b86af20753367c1d0579884a1225aa` into
`feature/self-edit-prose` and retains the initial prose cleanup. It uses the
general-change spec, frozen at SHA-256
`1ba7785ae1b2babf36a801f32ea666f03fa73ac3cf4b5296db5b5df16c83101d`.
The spec, dictionary, rubrics and historical experiment results are not edited.

Two fresh `codex exec` sessions using `gpt-5.6-sol`, medium effort, considered
code and documentation separately. They proposed caching the meaning grade
and removing a repeated rubric-change warning. Review retained those proposals
and identified additional local simplifications; no broad rewrite was needed.

The executable changes are:

- `filelevel.payload` scans and masks each distinct source once per call,
  rather than once per comment. Its cache is local to the call, so it cannot
  reuse stale source across reviews. Comment offsets and prompt text stay the
  same. The label-to-arm conversion also drops an intermediate dictionary.
- `commits.run` and `commits.rescore` use one local result writer for sorting,
  arm summaries and reports. File formats and case counts stay the same.
- `tiers.case_criteria` calculates the mean meaning grade once for both the
  recorded value and the precondition decision.
- `changes.summarize` states outcome precedence with explicit branches:
  blocked, failed, unassessed, then criteria passed. It also removes an unused
  loop binding.

The contribution guide now states the rule against changing a rubric to
improve scores in its evaluation section, without duplicating it in the
introduction. Other maintained prose was left alone where no additional
change was justified. New comments explain the shared writer and preservation
of source offsets.

### Checks

The 57 focused checks for mixed-content review, file-level judging, commit
scoring, tier scoring, runners and CLI dispatch passed. Added checks cover
source reuse within a call, isolation between calls, outcome precedence,
shared result ordering/case counts, and reuse of the mean meaning grade.

All 17 existing file-judge prompts match byte-for-byte. Rewriting the saved
20-commit results into a temporary directory reproduces `results.json`,
`summary.json` and `report.md` byte-for-byte. Markdown commands, examples,
links and numbers are preserved. No LLVM model experiment or smoke test was
run, and no historical artifact was overwritten.

These checks preserve the affected contracts; they do not require an identical
AST or prove correctness for all inputs. Raw editing proposals, preservation
records and the independent mixed-content review stay local under
`runs/self-edit-code/`. This cleanup is not a controlled estimate of the
general-change spec's effectiveness.

### Mixed-content review

One fresh `gpt-5.6-sol`, medium-effort judge reviewed seven changed code units,
the two new comments/docstrings, and the contribution-guide edit together
under the unchanged `change-rubric-v1` rubric. All applicable criteria received
deficit 0 and no blockers were reported. Clean and effective were not
applicable to code or other text; all four applied to the two comments.

The input SHA-256 is
`a59ae9d3a6de8a4f5b989c8db1787e632e368a74c6b910204a1208b3e7ab9ee8`.
This was a single review of the supplied before/after edits, not a blinded
ablation. It does not establish correctness or general effectiveness, and did
not assess every unchanged file or the earlier prose-only pass.
