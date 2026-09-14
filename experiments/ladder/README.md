# Four criteria, hardest last

Clean, effective, invasive, optimal, scored in that order, each only for the
cases that passed the one before. The design and its bars are in
[PROTOCOL.md](PROTOCOL.md). Aggregate results are here; detailed per-case
scoring stays in the private run directories as `tiers.json`.

The file and commit results below use the corrected v2 implementation.
The [protocol amendment](PROTOCOL.md#implementation-correction-2026-09-13)
documents the errors, replacements and preserved evidence. Rebuild these
aggregates with `python -m experiments.ladder.publish` from the project root;
it requires the local completed runs and makes no model calls.

## Where comments stand, 224 pairs

Re-analysis of the four finished runs of the
[150-comment study](../scaled/README.md). Those runs were made and read before
these criteria existed, so this tests no prediction.

| Criterion | Without spec | With spec |
| --- | ---: | ---: |
| Clean | 177/224 (79%) | 209/224 (93%) |
| Effective, of those | 60/177 (34%) | 65/209 (31%) |
| Invasive, of those | 31/60 (52%) | 35/65 (54%) |
| Clears all three | 31 (14%) | 35 (16%) |

The first step is large and holds in every run separately: comments that read
well are common, comments that are the right length and explain the right
thing are not. The spec moves clean sharply, from 79% to 93%, and moves
effective slightly the wrong way.

The second step does not hold. Invasive passes about half the time among
comments that already cleared effective, which makes it easier than the
criterion below it, not harder. 76 comments in the treatment arm pass invasive
while failing effective. Measured directly, generated comments name fewer
symbols from other files than upstream comments do (0.9 against 2.1 per hundred
words) and restate visible code at the same rate (0.02 for both). A comment
barely touches anything, so there is little for this criterion to catch. It is
reported because the proposal called for it, and because the result is the
answer to whether it belongs in a ladder for prose.

## Length, 250 pairs

From the 500-comment training generations, which used the neutral task
(`276ffbb0`) rather than the long-block task (`8adce2e0`) the 150-comment study
used. The neutral task asks for a comment; the long-block task says the
location needs a substantial explanation.

| | Original | Without spec | With spec |
| --- | ---: | ---: | ---: |
| Short locations (84) | 29.6 | 23.3 | 21.6 |
| Medium locations (83) | 65.1 | 30.2 | 27.5 |
| Long locations (83) | 149.7 | 38.0 | 35.2 |
| Spread across locations (sd) | 58.1 | 15.0 | 15.3 |
| Words gained per upstream word | — | 0.11 | 0.10 |
| Falls in the upstream length band | — | 24% | 19% |

A comment whose length followed the location would gain about one word for
each word upstream spent there. Both arms gain a tenth of that. The model
writes roughly one length everywhere and the spec does not change it.

Under the long-block task the same model produced comments about twice the
length of the originals. Under the neutral task it produced comments about a
third of their length. Neither task produced length that tracked the location,
and the earlier study's finding that the spec is "substantially more verbose
than upstream" is at least partly a property of the task it was given.

## All four criteria, 74 validation/test pairs

This re-analysis uses the existing validation/test generations and corrected
file-level judgments. One file's invalid judgment excludes four pairs from
fourth-rung coverage; none of those pairs passed the preceding rungs, so the
fourth-rung denominators below are unchanged. Meaning is reported separately,
not used as a gate: clearing this ladder does not establish factual accuracy.

| Criterion | Without spec | With spec |
| --- | ---: | ---: |
| Clean | 53/74 | 73/74 |
| Effective, of those | 20/53 | 23/73 |
| Invasive, of those | 9/20 | 12/23 |
| Optimal, of those | 5/9 | 7/12 |
| Clears all four | 5 (7%) | 7 (9%) |

## Placement: the model does decline

30 of the 60 frozen positions, both arms, 60 calls. The hypothesis written
before running was that the model would ask for a comment nearly everywhere
and barely distinguish the two kinds. That was wrong.

| | Without spec | With spec |
| --- | ---: | ---: |
| Asked for a comment where LLVM wrote one | 11/15 | 10/15 |
| Asked for one where LLVM wrote none | 4/15 | 3/15 |
| Agreement with upstream | 73% | 73% |
| Discrimination | +0.47 | +0.47 |

Both arms behave almost identically, so the spec makes no difference to the
decision. Reading the 16 disagreements, most are defensible in both
directions. Where it asked for a comment and LLVM had not, it named things
that genuinely are not obvious from the code: which references make a summary
ineligible for ThinLTO import, why a catchswitch redirects insertion to
another block. Where it declined and LLVM had written one, it usually pointed
at a comment already present a few lines away. Upstream silence was never
strong evidence, and these answers are the reason to say so plainly.

When it did write a comment it averaged 20 words, consistent with the length
finding above.

## A file's comments together

One call per file, all of that file's comments judged as a set against
[a second rubric](../../evaluation/file-rubric.md), 17 fresh corrected calls.
One test response quoted evidence absent from its assigned set; it is
preserved and excluded without a replacement call. All 17 earlier calls are
also preserved, but invalidated because their shared code context leaked
upstream comments. The rubric, spec and label seed did not change.

| | Files | Without spec | With spec | Upstream |
| --- | ---: | ---: | ---: | ---: |
| Test, valid sets with no noticeable deficit | 8 | 7 | 7 | 5 |
| Validation, sets with no noticeable deficit | 8 | 2 | 3 | 7 |

The two splits disagree sharply. Test files carry three or four comments,
validation files four to six, but this small comparison does not isolate the
cause. On validation the generated sets average redundancy deficits of 2.00
without the spec and 1.875 with it, against upstream's 0.125. Eight valid files
per split are too few for a general conclusion. Even the corrected judge sees
only six non-empty code lines after each comment, not the whole implementation.

## Commits: half clear the shape ladder

20 training commits, one arm, 20 calls. The comment spec is not guidance for
writing code, so there is nothing to ablate. The saved answers were rescored
offline with a shared original-to-final diff algorithm for both generated and
upstream changes; no new generation calls were made.

| | Count |
| --- | ---: |
| Answers that applied to the sources | 20/20 |
| Answers that overlapped the real change at all | 12/20 |
| Of those, no more invasive than the real change | 12/12 |
| Of those, in the right place (overlap 0.5 or more) | 10/12 |
| Mean overlap with the real change | 0.40 |

Every answer applied; eight missed the upstream change completely. Among
the twelve that overlapped it, all pass the invasiveness proxy and ten also
reach 0.5 overlap. Across all twenty, the median is 2 changed lines against
3 upstream. The earlier claim of larger generated changes was caused by
counting unchanged replacement anchors. It is withdrawn.

Nothing here was compiled or tested, so none of it says whether a change is
correct.

## Still to run

The other 30 placement positions, the validation and test commit splits, and
file-level judgments on any run with more comments per file. None of the
results above has been used to change the spec, the dictionary or the rubric.
