# Applying the spec to this repository

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
