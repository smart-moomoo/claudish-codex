# De-Claude whole changes

Rewrite the supplied input so a reader can understand its meaning and a
maintainer can follow its implementation. Preserve required behavior and every
substantive fact, condition, permission, comparison, uncertainty and implication.
This guide derives its prose rules from upstream Claudish, not the Codex guide.

## Work at the size of the input

Read the task, complete patch, changed files and supplied callers or tests
before editing. Record the behavior and explanations that must survive.
A large commit is one change: follow dependencies across files and check that
interfaces, implementations, tests and documentation agree. Do not turn it
into unrelated sentence-level edits. If context is missing, name the limit.

For prose, apply the imported instructions below. Reorder paragraphs, merge
repeated explanations and place warnings beside the action they qualify.
Explain the purpose before the taxonomy or history. Keep useful consequences
explicit; readers should not have to derive them from implementation details.
Preserve certainty in both directions. A supported guarantee must not become
a possibility, and an untested case must not become an incorrect case.

Before calling a passage redundant, distinguish the mechanism from what it
lets the reader do. A saved result and the ability to stop without paying for
that completed work again do different jobs in an explanation. Keep the
practical consequence explicit even when it follows logically from the
mechanism. If you remove its original sentence, identify the replacement
statement in your explanation; "the previous sentence implies it" is not a
replacement. Check this across the entire change so several local deletions
do not collectively remove the only statement of an important consequence.

For executable code, this section extends upstream's prose-only scope and
overrides its instruction to preserve code verbatim. Preserve required behavior,
not implementation. Remove unnecessary wrappers, duplicate state, speculative
options and abstractions that serve no actual caller. Keep abstractions that
enforce invariants. Follow ownership across files; do not reduce one file's
complexity by shifting unnecessary work to its callers. Preserve error paths,
public contracts, ordering and boundary cases. A smaller diff is not the goal.

Correct a factual error only when the supplied context establishes the error;
identify it and its evidence separately from stylistic changes. Do not silently
hedge an unsupported claim into a tautology, or invent missing historical reasons.
Report the specific property the evidence establishes. A hash comparison
checks recorded inputs; it does not prove a whole change safe or correct.
Do not certify the implementation as sound merely because a rewrite preserves
it. Separate inherited defects from defects introduced by the rewrite, and
name unresolved limits. Do not claim tests ran unless they did. Return a no-op when the input already
does the job; a visible change is not itself an improvement.

## Review the result against its contract

Review all four criteria, including when the prose already reads well.
Cleanliness and effectiveness apply to comments and docstrings. Invasiveness
and optimality apply to code, comments and other text. Correctness and meaning
preservation are separate requirements; a style improvement cannot compensate
for a broken contract. Word counts and patch sizes are descriptive, not grades.

For comments, state the action or relationship directly. A description that
only repeats a declaration usually adds no information. Delete a clause only
if no fact, condition, permission, uncertainty or implication is lost, or its
meaning remains explicit elsewhere. Read a long block as one explanation.
Several facts can share a sentence or paragraph without losing their distinctions.
Keep separate placement when readers need the information at different actions.
Check who does what to whom: clearer grammar must not reverse ownership, data
flow, binding or responsibility.

For code, preserve the required input domain and behavior, not every behavior
the supplied implementation happens to provide. Preservation of error paths
and boundary cases means those within this contract, not support for excluded
inputs. A stated precondition is usable evidence. Trace values and callers:
conversion or mutation can change what is known, and a canonical input does
not make every internal representation canonical.

For each check, fallback, helper, state variable or extra processing step added
by the supplied change or by your rewrite, identify the explicit requirement
or reachable failure it addresses. Compare it with a concrete simpler alternative
under the same contract. If removing it preserves required behavior, remove it.
A hypothetical future caller or an unsupported input is not justification.
Uncertainty alone does not justify adding a safeguard. If missing context prevents
a decision about existing code, name the exact missing contract or dependency;
do not certify the code as necessary or extend its input domain.

Support each addition with a well-motivated, in-scope test case: state the input
or execution condition, expected behavior and required failure without the
addition. Establish why that case belongs to the task before using it to justify
code. Reuse an existing test when it establishes the need. Add a test only for
an uncovered requirement or reachable failure, not a speculative edge case,
an excluded input or behavior invented to defend the implementation. Do not
add duplicate tests or new test machinery merely to satisfy this rule. For a
behavior-preserving simplification, use the applicable existing coverage and
trace why the removed work is redundant; no new behavior needs to be invented.
Distinguish a proposed test case from a test implemented or actually run.

A plausible purpose is not enough if the same purpose is already served
elsewhere. Reuse an available construction policy or common processing path
when it does the job. Check lock scope, side effects, invalidation and ordering
before removing work. Do not replace an established invariant with a fallback
or invent a framework for a hypothetical caller.

Trace the task's important cases through the complete result, including earlier
normalization and exceptional paths. Check whether apparently separate paths
need the same treatment. Do not describe a desired property as implemented
merely because the nearby branch looks right. If the supplied context establishes
a task-relevant defect, correct it within scope or report why it remains
unresolved; do not certify the result as complete.

Apply established comment corrections in the files, not only in the accompanying
explanation. An inherited false contract beside a changed interface or algorithm
is still relevant to that change. Check its declaration, implementation and
supplied examples together. Do not expand this into a cleanup of unrelated old
issues. Separate inherited defects, corrections and newly introduced regressions.

Read the whole result again for lost implications, changed certainty, repeated
explanations and cross-file inconsistencies. Return no edits when no justified
improvement remains. Do not claim tests ran or behavior was verified by execution
when the work was inspection only. The caller's output contract governs delivery
and overrides upstream's instruction to output only rewritten prose.

## Imported upstream prose instructions
