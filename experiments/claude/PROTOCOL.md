# Whole-change Claude rewrite study

The experimental unit is a complete input change, including parent versions,
input versions, the original task, full diff and explicit read-only context.
Do not crop large changes into independent hunks. Text examples use a complete
document or comment block. All model answers remain local, including failures.

## Conditions and scope

Use `claude-opus-5-5`, medium effort, through the local CLI in fresh sessions.
Compare the same input under a plain cleanup task, the exact pinned upstream
Claudish prose spec, and the upstream-derived counterpart. The model receives
no human target, other condition's output, judge rubric or provenance labels.
The plain task includes behavioral preservation and an output schema; it is
a practical no-spec baseline, not an empty prompt.

Upstream preserves executable code; the counterpart permits behavior-preserving
refactoring. Report this difference explicitly. A code-change advantage cannot
be attributed to better prose instructions under an identical code contract.
Authorship and a rhetorical style score are different questions. Commit trailers
are attribution evidence, not proof that every line came from a particular model.

Use small, medium and large cases. Large means at least four editable files and
500 added plus removed lines. Medium means at least two files or 100 changed
lines. Report exact sizes as well as these descriptive bands. Reject oversized
inputs explicitly; never silently truncate or cherry-pick hunks. Retain whole
documents, callers and tests when they are in the selected commit.

## Development and freezing

Start with a recorded fresh Claude explanatory document and public, Claude-
attributed repository commits. These are development data. Inspect complete
contrasts, including no-ops and regressions, and make at most one evidence-led
revision after the first training round. Freeze the revised guide, dictionary,
runner, rubric, task and selected cases before held-out evaluation.

Fresh held-out cases must not share repository/file paths with training,
including read-only context. Do not reuse the old LLVM held-out splits.
Keep all split manifests in the load operation so overlap is checked before
selecting a split. If held-out evidence changes a rule, retire those cases and
register a new holdout; do not repeat them and claim an untouched test.

## Fixed assessment

Use fresh `codex exec` judges, `gpt-5.6-sol`, medium effort, and the unchanged
`evaluation/change-rubric-v2.md` for every condition and round. Each judge sees
one anonymous candidate against its input, parent and context, with no condition
label or rewriting guide. Randomize case/condition execution order with seed 42.

Review complete files together. Cleanliness and effectiveness apply only to
comments/docstrings; invasiveness and optimality apply to all kinds. Python and
C/C++ comments receive a separate assessment with the full code still present.
Unsupported languages retain code review but have no extracted comment score.
Meaning loss, altered certainty and omitted supported reasons can block a change.
Report results by artifact kind and commit size; do not turn N/A into a pass.

Capture word/sentence metrics as descriptions, not optimization targets. No-op
rewrites are allowed but not automatically successful. Verify edit applicability,
file scope, nonoverlapping anchors, input hashes and recorded model identity.
This study does not execute generated code; correctness remains unestablished.
Focused tests validate the infrastructure, not the quality of model prose.

## Failures, cost and publication

Resume reuses saved successful calls and completed rows under identical inputs.
Never reroll failed or invalid responses automatically. Retain raw stdout/stderr,
including timeouts, and report all attempted cases. A parser repair may recover
an existing answer only with explicit provenance; preserve the original failure.

Publish pinned source metadata, selection, protocol, aggregate results and
iteration notes. Keep prompts, raw model answers, credentials, downloaded source
trees and generated patches under ignored `runs/`. CLI cost fields are reported
estimates, not a claim about subscription billing. No upstream writes or PRs.
