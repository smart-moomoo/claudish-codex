# Focused revision: require evidence for defensive additions

The user requested a revision of the defensive-preservation rule and a check
of the previous candidate's PhiValues loss. This is a targeted training check,
not another nine-case run or a promotion experiment.

Freeze `manual-candidate-v2-review.md` before inference. It replaces the previous
candidate's review section, leaving its other sources and upstream pin unchanged.
Require an explicit requirement or reachable failure and a motivated, in-scope
test case for added structure. Existing coverage may suffice; no speculative
input support, redundant tests or new test framework is required. Keep the
meaning-preservation test for explanations separate from code justification.

Use only the saved seed for `llvm-91aa5daec419`. Compare the maintained guide,
previous candidate and revised candidate in three independent forks of one
context-only acknowledgement. Budget: one context call, three rewrites with
Opus 5.5 medium and three independent GPT-6 Sol high reviews. Keep the existing
rubric, parent/seed input, tool isolation and 70% rewrite cache gate. No seed
regeneration, rerolls, smoke calls, execution of generated LLVM, or holdout use.
Stop scheduling on a failed call; retain all attempts and all regressions.

The rewrites receive no upstream solution, previous cleanup, review, case-specific
diagnosis or this document. Reviewers receive the usual historical reference,
but not guide labels or hypotheses. Inspect actual edits as well as grades.

The targeted question is whether the revision eliminates repeated operand-depth
lookups and avoids looking up the current phi until needed, without using stale
state across recursion or adding defensive code/tests. The previous candidate
returned no edits; the maintained guide made that simplification. Retain those
historical observations, but use the fresh sibling arms for the new comparison.
A single successful output establishes only a local result, not reliability or
the original two-case/no-worsening promotion gate. Keep the maintained guide
unchanged pending broader evidence.
