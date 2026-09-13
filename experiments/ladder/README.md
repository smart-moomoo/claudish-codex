# Four criteria, hardest last

Clean, effective, invasive, optimal, scored in that order, each only for the
cases that passed the one before. The design and its bars are in
[PROTOCOL.md](PROTOCOL.md). Aggregate results are here; detailed per-case
scoring stays in the private run directories as `tiers.json`.

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

## Still to run

Placement, the third part of effective, needs the 60 frozen positions in
`corpus/scaled-500/placement.json`. The file-level judgments for optimal and
the commit corpus in `corpus/commits` are described in the protocol. None has
been run.
