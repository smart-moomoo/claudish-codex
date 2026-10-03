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
