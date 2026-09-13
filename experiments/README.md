# Initial LLVM study

This page records the original short-comment series. Its references were only
12–38 words, mostly single sentences; it cannot establish long-comment quality.
See the separate [long-block resampling study](long-blocks/README.md).
Spec snapshots on this page record the earlier versions; the repository's
current spec was revised again for the [scaled study](scaled/README.md).

The project and experiment workflow are implemented. The initial study does
**not establish that the spec improves Codex's comments on unseen LLVM files**.
Training and validation showed some gains in meaning and descriptive measures;
the held-out evaluation did not confirm those gains. The current spec is an
experimental artifact, not a benchmark winner.

## Runs

All calls used `codex exec`, `gpt-5.6-sol`, medium reasoning, and Codex CLI
0.154.0. There were 78 distinct fresh sessions: 52 generation calls and 26
judge calls. The study used 14 distinct historical comment locations, with
the six training locations evaluated under three spec versions. There were
no repeated draws within a round. The final continuation used 12 calls;
completed runs from before the pause were not repeated.

The table shows mean deficit scores; **lower is better**, on a 0–4 scale.
Each arrow is that run's without-spec → with-spec comparison. Different
rounds contain different stochastic draws and should not be treated as a
controlled comparison between spec versions.

| Run | Paired cases | Meaning | Usefulness | Claudishness | Advisory screen |
| --- | ---: | ---: | ---: | ---: | --- |
| Round 01 | 6 | 1.33 → 1.00 | 0.83 → 0.83 | 0 → 0 | Not passed |
| Round 02 | 6 | 1.17 → 0.50 | 0.83 → 0.50 | 0 → 0 | Not passed |
| Round 03 | 6 | 1.17 → 0.67 | 1.00 → 0.33 | 0 → 0 | Not passed |
| Validation | 4 | 0.75 → 0.50 | 0.75 → 0.75 | 0 → 0 | Not passed |
| Held out | 4 | 1.00 → 1.00 | 0.75 → 1.00 | 0 → 0 | Not passed |

The final spec and judge rubric were frozen before validation and remained
unchanged for the held-out run. See [the freeze record](frozen-candidate.json),
[protocol](PROTOCOL.md), and [iteration notes](ITERATIONS.md). Private local run
directories contain the complete prompts, actual responses, anonymous-label
mapping, per-comment grades, reference links, and generated diffs; Git ignores
them. A line-wrapping issue in evidence validation was repaired by reaggregating
round 01's original responses, without repeating calls or editing scores.

## Distance from historical upstream comments

These are mean per-comment distances, not distances between corpus averages.
A smaller value means closer resemblance on that measure; it does not by
itself mean higher quality. All metrics were defined before generation.

| Measure | Validation without | Validation with | Held out without | Held out with |
| --- | ---: | ---: | ---: | ---: |
| Lexical Jensen–Shannon divergence | 0.696 | 0.645 | 0.409 | 0.699 |
| Absolute word-count gap | 5.75 | 10.75 | 8.00 | 11.00 |
| Absolute sentence-count gap | 0.50 | 0.50 | 0.50 | 0.50 |
| Absolute words-per-sentence gap | 4.08 | 5.58 | 4.50 | 3.50 |
| Absolute mean-word-length gap | 0.542 | 0.333 | 0.338 | 0.844 |
| Absolute long-word-fraction gap | 0.108 | 0.053 | 0.055 | 0.089 |
| Absolute hyphenated-word-count gap | 0.00 | 0.25 | 0.00 | 0.25 |
| Absolute semicolon-count gap | 0.00 | 0.00 | 0.00 | 0.00 |
| Absolute parenthesis-count gap | 0.00 | 0.00 | 0.00 | 0.00 |
| Absolute repeated-bigram-fraction gap | 0.062 | 0.023 | 0.010 | 0.010 |
| Absolute lexical-diversity gap | 0.076 | 0.100 | 0.035 | 0.073 |

Validation improved vocabulary distance, word-length distance, and repetition
distance, while word-count distance worsened. On held-out comments, only
words-per-sentence distance improved; several other distances worsened.
No uniform reduction in the gap has been demonstrated.

## What the actual comments show

In training, the initial spec sometimes compressed away useful detail. The
dictionary was revised to preserve local conditions, consequences, and
reasons, then to avoid narrating adjacent operations. In the final training
round, the switch-metadata comment described merging a removed case's weight
into the default weight instead of merely saying to update metadata.

In the held-out loop-membership case, both agents omitted why placing the
split after PHI nodes preserves LCSSA. The treatment's shorter statement also
received a worse usefulness score. In the PHI-handle case, both agents omitted
replacement with undef as a reason to use tracking handles. A style prompt
did not consistently recover the rationale in the human reference.

The baseline in `bbutils-dead-successors` exactly reproduced the original
upstream sentence, ignoring line wrapping, without receiving the hidden
comment. This is a possible memorization confound; the experiment cannot
distinguish memorization from independent reconstruction. Reference masking
and fresh sessions prevent direct exposure, not pretraining overlap.

The judge also made questionable distinctions between nearly equivalent
training comments, documented in [the iteration notes](ITERATIONS.md). Those
observations are construction-agent analysis, not human calibration. Original
grades remain intact. Upstream comments themselves sometimes received
deficits: historical human wording is reference material, not infallible prose.

## Interpretation and next evidence

Both arms almost always had zero style deficits, so this sample and rubric
provide little discrimination for Claudishness. The four-file corpus, single
draw per arm, possible memorization, same-model judging, and visible factual
reference limit the conclusion. The measured training gains cannot establish
improvement in a full coding workflow or across LLVM.

A future study should first collect real, human-labelled examples of unwanted
comment style and calibrate a new judge series against those labels. Expand
the corpus across files and near-duplicate families, retain immutable human
references, and include comments produced during actual code-editing tasks.
Use repeated draws and a new held-out set. The test cases exposed here must
be treated as development data if they influence further spec changes.
No further model calls or spec revisions were made after this held-out result.

## Verification and usage

The ten focused parser, code-preservation, and judge-contract tests passed.
Dictionary/spec synchronization and all 14 source/reference records were
verified. No smoke tests were run. The continuation did not repeat unchanged
tests or completed experiments.

The saved CLI usage events report 711,700 input tokens, including 209,920
cached input tokens, and 29,419 output tokens. They separately report 19,141
reasoning-output tokens; these fields are preserved as reported rather than
converted into a billing estimate. These totals cover the 78 experiment
calls, not the conversation constructing the project.
