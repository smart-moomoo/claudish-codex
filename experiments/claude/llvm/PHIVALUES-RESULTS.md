# Defensive-guidance revision: partial recovery, not solved

The revised candidate moves the current-phi lookup into the branch that needs
it. It still repeats operand-depth lookups, so it does not recover the full
simplification previously made by the maintained guide. No added defensive
branch, helper, fallback or test appears in this rewrite. Inspection found no
new behavior defect in the narrow edit; generated LLVM was not executed.

## Guidance change

[Candidate v2](manual-candidate-v2-review.md) replaces the previous candidate's
instruction to retain checks whose necessity remains unresolved. Added structure
must address an explicit requirement or reachable failure, supported by an
in-scope test case. Existing coverage can suffice. Unsupported inputs, speculative
edge cases, redundant tests and new test machinery do not justify additions.
The explanation-deletion test remains separate from code preservation.

The candidate was built from the previous candidate's source snapshot with the
normal Claude spec builder. Its dictionary and pinned upstream source did not
change. No case-specific code, symbols or lookup solution entered the guidance.

## What the three outputs did

All arms used the same saved seed, complete parent/seed files and task, in
independent forks of one context-only session. References, previous answers
and the targeted diagnosis were withheld. Claude used Opus 5.5 medium.

| Guide | Actual executable edit | Repeated operand lookups remain? |
| --- | --- | --- |
| Maintained | Changes the read-only operand-depth reference to a value. | Yes |
| Previous candidate | No edits. | Yes |
| Revised candidate | Copies operand depth by value and moves the current-phi lookup inside the updating branch. | Yes |

The revision avoids one map search when the operand's component is already
complete. Both keys exist at this point: the current phi was inserted on entry,
and the operand either already existed or was recursively processed. Reading
the operand value before acquiring the current-phi reference crosses no mutation.
The update still uses the same minimum under the same condition, including when
the two phi pointers alias. This supports the local edit by inspection.

However, the visit check, assertion and later subscript still search for the
operand separately. On an already-visited operand, that means two searches in
release builds and three with assertions enabled. The old successful control
cached the operand depth and refreshed it after recursion. The revision does
not do that. Redundant stack-top lookup/update work also remains.

The fresh maintained output did not repeat its historical simplification. The
previous candidate again returned no edits. Preserve this variability: the
revised output improves on these fresh siblings, but one run does not establish
that the new rule reliably causes the improvement. Nor does this experiment
separate the effect of the test-case rule from the other wording changes.

## Test justification is still not established

The revised response says existing PhiValues tests cover these paths, but its
input contains only `PhiValues.h` and `PhiValues.cpp`, with no supplied tests.
That coverage claim is unsupported by the experiment context. It did not claim
to run tests, and added none; neither fact demonstrates compliance with the new
test-evidence requirement. Its statement that each key is looked up once also
overlooks the earlier operand searches. These explanation problems are recorded
separately from the file-only independent reviews.

## Independent reviews

All three fresh GPT-6 Sol high reviews completed and passed the fixed evidence
validator. All identify inherited incomplete removal of redundant searches;
none identifies a newly introduced correctness regression. For `PhiValues.cpp`,
T3 deficits are 0 in every arm and T4 deficits are 3, 2 and 3 for maintained,
previous and revised respectively. The unchanged header scores 0 in both tiers.
There are no changed comment artifacts, so T1 and T2 are not assessed here.

The previous no-op receives a lower severity than either edited output despite
retaining the same redundant operand work. Record these raw judgments rather
than interpreting that severity difference as evidence of a new defect caused
by the revision. The actual diff supports a narrower conclusion: one unnecessary
lookup is avoided, the other targeted redundancy remains, and aggregate grades
do not demonstrate improvement.

All seven completion receipt trees were verified, along with distinct sibling
sessions sharing the unchanged context-only parent and the frozen candidate
build. No generated LLVM code was compiled or executed. No model processes
from this experiment remain running.

## Scope and status

This targeted training check is not a nine-case promotion run. Keep the
maintained guide unchanged. The revision is available as an experimental source
and generated snapshot, not promoted based on a partial recovery on one input.
No holdout cases were used and no additional iteration was launched.

Candidate SHA-256:
`b94858066b9087a4c019145ce3c256dfe56649fc96031144f6d138e841fe0a83`.
Maintained guide SHA-256:
`3d0cf6cfa1ee58a1c432d642d040ce6ee443e1db9b4970f38c97fe169a8a0a72`.

The initial sandboxed context call produced connection retries and no model
answer; it was stopped and retained. [Recovery record](PHIVALUES-RECOVERY.md)
documents the single network-enabled retry with an identical frozen plan.
The completed comparison used one context call and three rewrites. Total
reported Claude usage for those four completed calls: 8 uncached input tokens,
33,683 cache-write input tokens, 47,925 cache-read input tokens and 6,054 output
tokens. The failed attempt returned no usage receipt. Do not infer zero usage
for it or equate these token counts with subscription quota.

All three rewrites exceeded the 70% cache-read gate: 75.1%, 72.5% and 71.5%.
Including context loading, 58.7% of reported input tokens came from cache.
Raw files, outputs, diffs, session evidence and reviews remain private under
`runs/claude-llvm/manual-challenge/phivalues-revision-2-network/`.

## Subsequent publication decision

After this evaluation, the user requested replacing the old Claude artifact
instead of publishing a separate v2. The exact evaluated revision is now the
sole [Claude artifact](../../../specs/artifacts/claude.md), with its
[editable source](../../../specs/claude-base.md). The earlier status above
records the experiment's decision at completion. This publication change does
not change the findings, satisfy the broader promotion gate or add new evidence.
