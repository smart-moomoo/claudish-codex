# Scope of the four criteria

The general-change guide is `specs/codex-changes.md`. Its shared instructions
come from `specs/changes-base.md`; its comment-specific section comes from
`specs/base.md` and the existing dictionary. `build-spec` generates both this
guide and the unchanged comment-only `specs/codex-comments.md`.

| Criterion | Comment or docstring | Other text | Executable code |
| --- | --- | --- | --- |
| Clean | Wording and structure | Not applicable | Not applicable |
| Effective | Need, scope, detail and length | Not applicable | Not applicable |
| Invasive | Unnecessary reach, duplication | Unnecessary edits, duplicated guidance | Unnecessary scope, coupling, abstractions |
| Optimal | Placement and consistency | Organization and consistency | Ownership, interfaces, caller impact and fit |

These are applicable review criteria, not four mandatory gates for every
artifact. Code and text start at invasiveness. A failed comment does not hide
code from review, and not-applicable criteria never count as passed. Every
applicable criterion is reviewed independently; results are counted by kind
rather than pooling different kinds into one pass rate.

Correctness, factual accuracy, safety and task completion are separate
requirements. A code cleanup may alter structure, helpers and control flow
while preserving required behavior. Removing safeguards or necessary tests
to shorten the diff is not a successful cleanup. Verify affected behavior
with focused checks; do not require an unchanged AST for a code refactor.

## Input format

`review-change` takes a JSON object with exactly `task` and `artifacts`.
Each artifact has a unique ID, a kind (`comment`, `text` or `code`), a path,
before text, after text, and surrounding context. All six fields are strings.
Paths identify evidence; the reviewer does not open or modify them.

This synthetic example illustrates the format, not a completed model review:

```json
{
  "task": "Remove an unnecessary wrapper without changing the result.",
  "artifacts": [
    {
      "id": "implementation",
      "kind": "code",
      "path": "example.py",
      "before": "def result():\n    return value()\nanswer = result()\n",
      "after": "answer = value()\n",
      "context": "result is private and has no other callers. value is supplied by the caller."
    },
    {
      "id": "explanation",
      "kind": "comment",
      "path": "example.py",
      "before": "# Use the result wrapper.\n",
      "after": "",
      "context": "The comment immediately precedes the assignment to answer."
    },
    {
      "id": "documentation",
      "kind": "text",
      "path": "README.md",
      "before": "The result wrapper calls the supplied value function.",
      "after": "The assignment calls the supplied value function directly.",
      "context": "This section describes how the assignment obtains its value."
    }
  ]
}
```

Provide independently reviewable units. Split mixed files into typed units
and include relevant callers, surrounding prose and cross-file relationships
as context. The caller is responsible for classification, completeness and
authorship; the tool does not detect AI-generated content or certify that a
claimed refactor is safe. Unchanged before/after pairs are allowed so a no-op
can still be assessed against a task. Empty before/after strings represent
additions/deletions. Empty context is allowed, but may leave fit unassessed.

## Outputs and limitations

One fresh `codex exec` call reviews the supplied units together with
`gpt-5.6-sol`, medium effort, and `evaluation/change-rubric-v1.md`. The rubric
is independent of the generated spec and dictionary. No personal instructions
or prior judge responses are supplied to the judge.

The output directory contains the input, rubric, hashed manifest, raw call
artifacts and `review.json`. Existing directories are refused. Invalid answers
remain in the raw call directory and mark the run failed; they are not rerolled.

An applicable criterion has a 0–4 deficit, explanation and cited evidence,
or a null deficit when unassessed. Deficits below 2 pass. Text/code must have
null raw clean/effective assessments, reported as `not_applicable`. Evidence
identifies an artifact, before/after/context source, and an exact quote;
noticeable deficits require evidence. Cross-artifact evidence is allowed.

The outcome is `blocked` if the judge reports apparent correctness, safety,
factual or task-completion problems; otherwise `fail`, `unassessed` or
`criteria_passed`. None establishes correctness. The tool runs no code, does
not verify supplied test claims, and cannot certify readiness to merge.

## Relationship to the existing experiments

The comment grader and `score-tiers` retain their original scales and ladder
aggregation. Comment identifier coupling is a proxy for invasiveness;
file-comment consistency is a limited proxy for fit. Neither measures every
aspect of a mixed-content change.

`commit-run` measures changed positions and overlap with an upstream patch.
These are shape and placement proxies, not proof of correctness or optimal
architecture. For a future paired code experiment, explicitly supply the new
guide:

```sh
python -m claudish commit-run --split train --corpus-dir corpus/commits \
  --spec specs/codex-changes.md --out runs/code-guidance
```

Do not relabel historical baseline results as an ablation of this guide.
The broader guidance and review contract have no empirical validation yet.
Future changes need a new frozen training protocol, independent review and
fresh held-out data before any generalization claim. Historical outputs,
rubrics, source references and protocols remain unchanged.
