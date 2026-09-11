# Spec construction notes

## Round 01: initial simplification rules

Six paired training tasks, fresh `gpt-5.6-sol` / medium calls in both arms.
All generated comments received zero style deficits; there is no measurable
Claudishness improvement on this small sample. The upstream comments were
occasionally informal or structurally awkward, so upstream is a reference
distribution, not a requirement to imitate every sentence.

The initial spec reduced mean comment length from 19.83 to 14 words, versus
21.67 upstream. Mean meaning deficit improved from 1.33 to 1.00, but usefulness
stayed at 0.83. Inspecting comments showed lost detail: the switch comment said
only to update metadata, and the search-table comment omitted the choice of
byte-sized storage. Both arms missed the leading-zero limitation of numeric
comparison. Shorter prose alone is not the desired outcome.

The final judge quotation joined a wrapped source line. Aggregation initially
rejected it because it required byte-contiguous evidence. The validator now
allows whitespace normalization only; it still rejects invented quotations.
The unchanged stored responses were reaggregated with `replay`; no scores,
prompts, outputs or judge rubric were edited, and no model call was repeated.

## Round 02 hypothesis (written before running)

Retain the original anti-rhetoric rules, add `preserve-local-facts` and
`explain-local-choice`, and strengthen the base instruction to preserve
conditions, consequences and non-obvious reasons. The examples are synthetic
and do not copy LLVM reference comments. Expected benefit: reduce missing
facts and generic narration while keeping style deficits low. This may need
more words. Do not tune against validation or test results.

## Round 02 result

Meaning deficit fell from 1.17 without the spec to 0.50 with it, and usefulness
from 0.83 to 0.50. There were no paired meaning regressions under the fixed
judge. The mean absolute word-length gap to upstream fell from 0.80 to 0.64
characters and long-word-fraction gap from 0.081 to 0.059. Style grades remained
at zero, so the strict style-improvement screen still did not pass.

Some generated comments grew to describe neighboring operations, and mean
absolute word-count gap increased from 6.50 to 9.67. The switch-metadata output
also asserted a consequence for the opposite branch that deserves scrutiny;
the judge did not flag it. This is an example of why its scores are advisory.

## Round 03 hypothesis (written before running)

Limit explanations to the comment's local operation, preserve essential
reasons or exceptions, and explicitly check claims about the opposite branch.
Add `keep-explanations-local`. Correct the synthetic seed examples so the
before text explicitly contains facts retained in the after text. This is the
last training revision in the initial study. The candidate will be frozen
before evaluation on the other files.

## Round 03 result and frozen candidate

The treatment's meaning deficit was 0.67 versus 1.17 without the spec;
usefulness was 0.33 versus 1.00. Mean words per sentence moved closer to the
reference (absolute gap 5.67 versus 6.33), and mean word-length gap fell from
0.78 to 0.68 characters. Other measures did not improve: word-count gap was
8.00 versus 6.67, lexical distance slightly increased, and the treatment had
one minor vocabulary deficit. Broad style superiority is not established.

The judge flagged a paired meaning regression in `local-dead-operands`: it
accepted "If the operand is an instruction ... add it to the worklist" but
penalized "Add an operand to the worklist if it is an instruction ...". The
construction agent considers that distinction inconsistent with the shared
condition and action. This is an AI review observation, not a human rating;
the original score remains unchanged. The conservative screen stays false.

Freeze round 03 as the **experimental default**, not a proven winning spec.
It fixes the earlier vague switch description and the synthetic examples,
and will now be assessed without further tuning on the other files. Both
validation and test results will be reported, including failures. No result
from those splits has been inspected at this point.

## Validation result

The frozen round-03 spec was evaluated on four comments in LoopInfo.cpp.
Mean meaning deficit improved from 0.75 to 0.50, with no paired meaning
regressions. Mean usefulness stayed at 0.75, and all generated style grades
were zero. The average lexical distribution distance to the reference fell
from 0.696 to 0.645; mean absolute word-length gap fell from 0.542 to 0.333
characters. Word-count gap increased from 5.75 to 10.75, so the treatment did
not move uniformly toward the human references.

The unique-exit comments in both arms omitted the original implementation's
rationale. The treatment described the canonical induction variable more
precisely, but its hoisting comment still omitted the specific control
dependency. These are recorded limitations, not reasons to tune on validation.
The spec and rubric remain unchanged for the held-out evaluation.

Work was paused at the user's request after validation had completed. No
experiment processes remained running during the pause. On continuation,
only the previously planned held-out evaluation was started; completed
training and validation calls were not rerun.

## Held-out result and end of the initial study

Four cases from BasicBlockUtils.cpp were evaluated with the same frozen
spec. Mean meaning deficit tied at 1.00. Mean usefulness deficit increased
from 0.75 to 1.00. All generated style grades were zero, and the advisory
promotion screen did not pass. Words-per-sentence distance improved, while
word-count, mean-word-length and lexical distances worsened. The complete
study is summarized in [README.md](README.md).

No further tuning was performed. The project ships the frozen spec as an
experimental artifact alongside the negative held-out result. The planned
initial iteration series is complete; future tuning requires new evidence
and a new held-out set. All 78 experiment calls finished, each in a distinct
fresh session using the requested model and effort.
