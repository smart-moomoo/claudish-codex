# Working on Claudish Codex

Use Python 3.11+ and the standard library. Run commands from this directory or
pass the project directory with `--root`.

For text, comments and code, follow `specs/codex-changes.md`. Cleanliness and
effectiveness apply only to comments and docstrings; invasiveness and
optimality apply to all three kinds. Preserve required behavior, not the
implementation itself, when refactoring code.

Edit `specs/changes-base.md` for shared change guidance. Comment guidance comes
from `specs/base.md` and `dictionary/entries.json`. Rebuild both generated specs
with `python -m claudish build-spec`; do not hand-edit them. The comment-only
`specs/codex-comments.md` remains available for frozen comment experiments.

All model calls use `codex exec`, `gpt-5.6-sol`, medium reasoning unless the
user explicitly changes those settings. Start fresh sessions for generation
and judging. Do not let personal instructions, reference comments, or previous
outputs enter the generation environment. Keep the judge rubric fixed during
a spec iteration. Preserve all real outputs, including regressions.

Tune only on training data. Freeze choices before validation and test runs.
Once test results influence a choice, retire that test split as a holdout.
Never fabricate human comments, authorship attestations, ratings or model runs.

Use focused deterministic checks for parser, grading and corpus invariants.
Do not run smoke tests, make intermediate approval stops, or repeatedly run
unchanged tests. Never submit generated comments to upstream LLVM as part of
an experiment.
