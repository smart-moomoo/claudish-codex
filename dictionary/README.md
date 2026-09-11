# What this dictionary does

This dictionary changes the instructions Codex uses to write code comments.
It is not a glossary used only by a website, and it is not a word-replacement
engine.

`python -m claudish build-spec` combines `specs/base.md` with every entry in
`entries.json`. Each entry contributes its guidance, before/after example and
exceptions to `specs/codex-comments.md`. The generated spec is the file users
load through AGENTS.md. CI rejects a dictionary change with a stale spec.

The `signals` field supplies search hints to contributors; it does not assign
grades or ban words. The `evidence` field links to real failures or upstream
sources. The independent judge rubric does not ingest this dictionary, so
adding an entry cannot change the rules used to score that entry's effect.

Before/after examples are synthetic and must preserve the same facts. Actual
human reference comments remain verbatim in the LLVM corpus, with provenance.
See [the contribution workflow](../CONTRIBUTING.md) and
[the recorded iterations](../experiments/ITERATIONS.md).
