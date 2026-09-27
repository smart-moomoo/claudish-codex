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

## Review at the right scope

Cleanliness and effectiveness apply to comments and docstrings: do they state
the explanation directly, and is that explanation needed here at this length?
Invasiveness and optimality apply to prose, comments and code: is every part
needed, and does the whole result fit its readers, callers and owning component?
Meaning and behavioral correctness remain separate requirements. Word counts
and patch sizes describe changes; they do not establish quality or authorship.

Read the complete result again. Check for lost implications, changed certainty,
orphan conclusions, contradictory documentation and cross-file regressions.
The caller's output contract governs delivery (for example JSON edits); it
overrides upstream's final instruction to output only rewritten prose.

## Imported upstream prose instructions
