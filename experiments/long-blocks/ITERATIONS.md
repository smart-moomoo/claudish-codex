# Long-block iteration log

## Round 01: original seven-rule spec

Four training pairs and four judges completed before the usage pause. Keep
these twelve calls; do not rerun them. The existing spec produced mean
Claudishness 0.25 versus 0.50 without the spec, and simplicity 0.75 versus 1.00.
Meaning tied at 1.00, but usefulness worsened from 0.00 to 0.25 and the loop
header case had a paired meaning regression. The advisory screen did not pass.

Unlike the one-line study, the new task produced real multi-paragraph blocks:
means of 259 words without the spec and 215.75 with it, versus 166.25 in the
historical references. Reference counts include IR/example tokens. A shorter
block alone is not an improvement.

Training observations motivating the one permitted revision:

- Loop-header treatment describes an approximate backedge destination as if
  it establishes a required path property, and adds a claim about non-natural
  cycles not established by the supplied context. Both arms spend space on
  downstream consumers while missing useful limitations of the approximation.
- Adjusted-pointer treatment explains many implementation details but omits
  reuse of an encountered i8 pointer in the fallback. Baseline adds a plausible
  optimization benefit not established by the task. A long explanation can
  simultaneously overexplain and omit an important fact.
- Both pre-split comments omit the return-value contract. The upstream block
  instead explains why this must be a preprocessing step and illustrates the
  interaction with a concrete example.

These are construction-agent observations and LLM grades, not human ratings.
The judge's objection to “provenance” is not adopted as a word ban: provenance
can be a precise compiler term. Nor is every judge omission necessarily a
material defect. Keep original scores and explanations visible.

## Round 02: scope and claim strength

Before round 02 generation, replace the base's one-sentence preference with
scope-sensitive guidance for local versus algorithm/function comments. Keep
contracts and meaningful fallbacks; avoid touring every statement. Add two
dictionary rules: organize-long-explanations and preserve-claim-strength.
Their examples are synthetic, not copied upstream or generated evaluation
outputs. The revision uses training evidence only.

The generation task, cases, contexts, model, effort and judge rubric are
unchanged. Both arms get fresh calls, so differences between rounds also
include sampling variation; do not present them as a controlled same-output
comparison of spec versions. This is the only revision permitted by the
long-block protocol. Freeze the selected candidate before validation/test.

Round 02 completed with all twelve calls. Within this round, Claudishness
improved 0.75 → 0.00, simplicity 1.25 → 0.00, meaning 1.25 → 1.00, and
usefulness 0.25 → 0.00. There were no paired meaning regressions; three
simplicity wins and one tie. The advisory screen passed. Mean length was
258.75 → 210.25 words, versus 166.25 upstream.

All four treatment comments still received meaning deficit 1. The pre-split
comment still misses why ordinary partition rewriting loses information.
Loop-header comments still omit examples of profitable cases the conservative
policy rejects. The judge did not flag the same omissions consistently across
rounds, so numerical gains are not proof that every targeted problem was fixed.

Select round 02 for the predeclared validation/test evaluation. The immutable
[freeze record](frozen-candidate.json) precedes both runs. No further revision
is allowed in this series. The candidate remains experimental even though its
training screen passed. Qualitative examples will be the three longest test
references, selected by length before test generation rather than by outcome.

## Validation: no retuning

All twelve validation calls completed with the frozen round-02 spec. Mean
Claudishness improved 0.50 → 0.25 and simplicity 1.25 → 0.50, but meaning
worsened 1.75 → 2.00; usefulness tied at 1.25. Two paired meaning regressions
were recorded, so the advisory screen failed.

The lattice-intersection treatment claimed to prefer the strongest retained
information even though the reference explicitly disclaims maximal precision.
The non-local-dependence treatment added incorrect cache invalidation details.
Both atomic-memory comments summarized the wider scan instead of explaining
the release/acquire rationale at the target. That rationale is historical
information not readily recovered from the supplied code; do not label its
omission solely a writing-style failure.

These failures do not trigger another revision. The predeclared held-out run
uses the exact same frozen spec, task and rubric. The long-comment instruction
and broad code contexts may themselves encourage overly broad walkthroughs;
this is a limitation of the reconstruction task, not an uncontrolled change
between arms or evidence about every ordinary coding workflow.

## Held-out result and close of this series

The final twelve calls completed with the frozen candidate. Claudishness
improved 0.75 → 0.25; simplicity improved 1.00 → 0.75; meaning stayed 1.50 and
usefulness stayed 0.50. There were no paired meaning regressions. Simplicity
had two wins, one tie and one loss, so the mean improvement was not uniform.
The held-out screen passed, but the combined eight unseen cases fail the
screen because the two validation meaning regressions remain.

The longest reference, negative-offset alias analysis, is the simplicity loss.
Both arms omit the warning about noalias arguments/calls. Object-size prose
is more direct with the spec but still repeats adjacent alignment commentary.
Loop-traversal prose improves in style but still misses the pass-manager
rationale. The upstream switch TODO is itself stale relative to code. Full
text for these three cases remains in the private local `examples.md` artifact,
selected by reference length as recorded before the test run.

The [audit](audit.json) verified all 48 fresh calls and the frozen input hashes.
The continuation used 36 new calls and did not repeat round 01 or unchanged
tests. The main spec remains the nine-rule experimental candidate, not a
proven overall improvement. No spec/dictionary/rubric changes were made from
validation or test results. Future use of these failures for tuning retires
the current test split as a holdout. No further model calls in this series.
