# Codex changes: text, comments and code

Apply this guide when writing or revising any project artifact. Preserve the
task's requirements and existing behavior unless the task asks to change them.
Preserving behavior does not require preserving the implementation: refactor
code when the change is justified and verify the affected behavior.

## Which criteria apply

| Criterion | Comments and docstrings | Other text | Executable code |
| --- | --- | --- | --- |
| Clean: clear wording and structure | Yes | Not applicable | Not applicable |
| Effective: needed explanation, scope and length | Yes | Not applicable | Not applicable |
| Invasive: unnecessary changes and dependencies | Yes | Yes | Yes |
| Optimal: placement and fit in the surrounding project | Yes | Yes | Yes |

These criteria have a proposed order, not a proven ranking of difficulty.
For comments, consider all four. For text and code, start with invasiveness;
the first two criteria are not automatic passes. A failure in a comment does
not prevent reviewing code elsewhere in the same change.

Correctness, factual accuracy, safety and task completion are requirements
for all artifact types. None is established by a style score or a small diff.
Missing context or verification leaves a conclusion unassessed, not passed.

## Invasiveness: all artifacts

Make the changes needed for the task, including necessary tests and
documentation. Avoid unrelated edits and new dependencies without a concrete
need. Judge scope against the requested outcome, not line count alone: a
shorter patch that omits required work is not less invasive in a useful sense.

For code, use existing interfaces and helpers when they fit. Remove unnecessary
wrappers, duplicate state and speculative abstraction only when doing so
simplifies the requested work without breaking contracts. Do not introduce a
framework or general-purpose extension point for a single known use. Keep
abstractions that enforce invariants or make actual callers easier to maintain.

For comments, explain the local reason or contract without repeating nearby
explanations or depending on unrelated implementation details. Retain
conditions, examples and caveats needed to understand the code.

For other text, change the relevant sections and preserve necessary facts,
commands, links and qualifications. Avoid duplicating guidance across files.
Do not rewrite historical evidence, provenance or reference material to make
it agree with a current conclusion.

## Optimality: all artifacts

Put each responsibility where its owner and readers expect it. Follow the
project's established interfaces, terminology and document organization.
Check how the change interacts with nearby code, comments and documentation,
not just whether the edited fragment looks reasonable on its own.

For code, keep behavior with the component that owns it, reuse suitable local
patterns, and avoid moving complexity into callers. Consider error handling,
boundary cases and maintenance across the affected call sites. Preserve public
contracts unless changing them is part of the task.

For comments, place the explanation at the relevant operation or contract.
Check for contradictions and unnecessary repetition across the file. Allocate
detail according to what each location needs, not a uniform length target.

For other text, put instructions where readers perform the task, keep related
guidance consistent, and link to a maintained source instead of copying it
when that is practical. Preserve enough context for the document to stand on
its own.

Here, optimal means justified fit among the alternatives visible in the
supplied context. It is not a claim of a globally best solution. Record the
tradeoff and any missing context instead of asserting certainty.

## Applying and checking changes

Inspect the relevant implementation before editing. Keep unrelated work and
private artifacts out of the change. Check behavior and contracts affected by
code refactoring; an identical AST is appropriate for a prose-only edit, not
a requirement for code cleanup. Use focused checks proportional to the change.
Never invent test execution, human approval, model judgments or evidence.

The following dictionary-derived guidance applies only to comments and
docstrings. It does not add cleanliness or effectiveness scores for other text
or executable code.
