# Codex changes: preserve meaning, improve the whole result

Complete the requested task while preserving its requirements. For a prose
rewrite, preserve meaning; for a code refactor, preserve required behavior.
Neither requires preserving the original sentences, paragraphs or implementation.

## Work from the whole task

Read the relevant document or implementation and its callers before editing.
Record the facts, conditions, permissions, uncertainty, implications and
contracts the result must preserve. Separate a requested behavior change or
an evidenced factual correction from a rewrite that should keep meaning.

Choose the organization before changing individual sentences or statements.
For a README, explain what the project does, show the first useful action,
then provide the concepts and evidence the reader needs to go further. Group
study results by the question they answer, not by when the studies happened.
Move, merge or delete paragraphs when that improves the reader's path, retaining
their distinct facts and qualifications. Use linked detail for secondary tasks;
do not move essential warnings away from the action they qualify.

For code, keep behavior with the component that owns it. Reuse suitable local
interfaces and patterns. Remove duplicate state, unnecessary wrappers or
speculative extension points when they complicate the requested work. Retain
abstractions that enforce invariants or serve actual callers. Inspect error
handling, boundary cases and caller impact before changing structure.

## Apply the criteria at their proper scope

| Criterion | Comments and docstrings | Other text | Executable code |
| --- | --- | --- | --- |
| Clean: direct wording and coherent explanation | Yes | Not applicable | Not applicable |
| Effective: needed facts, reasons, scope and detail | Yes | Not applicable | Not applicable |
| Invasive: unnecessary changes or dependencies | Yes | Yes | Yes |
| Optimal: organization, placement and fit | Yes | Yes | Yes |

For comments, consider all four criteria. For other text and code, start with
invasiveness; the first two are not automatic passes. The shared prose
principles guide writing in any document without adding cleanliness or
effectiveness scores for non-comment text. Review the remaining applicable
criteria even if an earlier one fails; a failed comment must not hide a code
problem elsewhere in the change. This is a proposed order, not a proven ranking.

Invasiveness concerns unnecessary work and dependencies, not the smallest
diff. Include the code, tests, explanations and cross-file updates the task
needs. Preserve unrelated user work, commands, links, provenance and historical
evidence. Keep each instruction in a maintained location rather than copying
it across documents without a reader need.

Optimality concerns the whole result. A locally clear paragraph in the wrong
place still fails the reader. Check entry points, paragraph order, repeated
explanations, terminology and transitions across the document. For code, check
ownership, interfaces and the burden on callers. State the relevant tradeoff;
"optimal" here means justified fit in the available context, not proof of a
globally best solution.

## Check meaning and behavior

Compare the result with the preservation record, including explicit reasons
and implications. Check certainty in both directions. Account for removed
clauses and moved paragraphs; flag factual corrections with their evidence.
Then read the complete result for coherence, not just the changed lines.

Verify behavior and contracts affected by code changes with focused checks.
An unchanged AST can check a prose-only edit; it is not a requirement for code
refactoring. Correctness, factual accuracy, safety and task completion apply
to every artifact type and are not established by a style score or a small
diff. Missing evidence leaves a conclusion unassessed. Never invent tests,
reviewer approval, model results or reference material.
