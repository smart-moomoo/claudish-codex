# Long-block LLVM study

Long-block sampling exposed style problems the one-liners missed. The revised
spec improved average style scores on unseen blocks, but did **not** establish
a safe overall improvement: two validation cases regressed in meaning. The
spec remains experimental. Three full-length contrasts, including a simplicity
regression, remain in the private local artifacts alongside the complete
reports. The aggregate results are published below.

The resampling protocol is in [PROTOCOL.md](PROTOCOL.md); source selection and
context boundaries are in [the corpus](../../corpus/long-blocks/README.md).
This series is separate from the initial 12–38-word study. Every reference is
an intact historical LLVM block of 102–263 words, not a generated expansion.

## Training and frozen choice

The first training run used the existing seven-rule spec
unchanged. One training-derived revision added scope-sensitive long-block
guidance and rules for organizing explanations and preserving claim strength.
The second training run passed the advisory screen and
was [frozen](frozen-candidate.json) before validation and test. See
[ITERATIONS.md](ITERATIONS.md) for the evidence and unresolved failures.

Scores are mean deficits on a 0–4 scale; lower is better. Arrows compare fresh
without-spec → with-spec outputs within a run, not the same outputs across
versions. Every run used four pairs, one draw per arm. Only the first two runs
were used for tuning; the same frozen candidate was used for both later runs.

| Run | Claudishness | Simplicity | Meaning | Usefulness | Screen |
| --- | ---: | ---: | ---: | ---: | --- |
| Round 01 | 0.50 → 0.25 | 1.00 → 0.75 | 1.00 → 1.00 | 0.00 → 0.25 | Fail |
| Round 02 | 0.75 → 0.00 | 1.25 → 0.00 | 1.25 → 1.00 | 0.25 → 0.00 | Pass |
| Validation | 0.50 → 0.25 | 1.25 → 0.50 | 1.75 → 2.00 | 1.25 → 1.25 | Fail |
| Held out | 0.75 → 0.25 | 1.00 → 0.75 | 1.50 → 1.50 | 0.50 → 0.50 | Pass |

The frozen candidate is experimental, not a promoted winner. Every treatment
comment in round 02 still had a meaning deficit. Validation improved style but
had two paired meaning regressions. The held-out run passed the advisory
screen, with unchanged meaning/usefulness, but that does not erase the
validation regressions. All four runs completed; no incomplete calls are
counted as evidence.

## Eight unseen blocks

Validation and test both used a candidate frozen before either run. Their
combined result below is descriptive, not a new independent experiment or a
statistical significance claim. Training observations are excluded. See the
machine-readable [unseen summary](unseen-summary.json).

| Mean deficit | Without spec | With spec | Upstream |
| --- | ---: | ---: | ---: |
| Claudishness | 0.625 | 0.250 | 0.000 |
| Words | 0.625 | 0.125 | 0.125 |
| Structure | 0.875 | 0.375 | 0.500 |
| Simplicity | 1.125 | 0.625 | 0.750 |
| Meaning | 1.625 | 1.750 | 0.250 |
| Usefulness | 0.875 | 0.875 | 0.000 |

Simplicity improved in five cases, tied in two, and worsened in one. Meaning
worsened in `long-lvi-intersection` and `long-memdep-nonlocal-query`.
The combined advisory screen therefore fails. All eight treatment comments
have nonzero meaning deficits; improved wording is not equivalent to complete
or correct maintenance documentation.

The lattice-intersection comment overclaims precision. The non-local-query
comment adds incorrect cache details. Both atomic-memory comments omit the
release/acquire rationale, while both loop-traversal comments omit why folding
and merging would threaten pass-manager invariants. These are materially
different failures from unnecessarily formal vocabulary.

## Distance from the actual upstream blocks

Mean length on the eight unseen blocks was 217.4 words without the spec,
189.9 with it, and 175.1 upstream. The table reports mean per-comment absolute
gaps, not the difference between those averages. Smaller distances mean closer
resemblance on that feature, not necessarily higher quality.

| Distance to upstream | Without spec | With spec |
| --- | ---: | ---: |
| Word-count gap | 67.250 | 55.750 |
| Sentence-count gap | 2.875 | 2.500 |
| Paragraph-count gap | 1.875 | 1.750 |
| Mean-word-length gap | 0.886 | 0.785 |
| Long-word-fraction gap | 0.0688 | 0.0542 |
| Repeated-bigram-fraction gap | 0.0525 | 0.0432 |
| Lexical Jensen–Shannon divergence | 0.589 | 0.599 |

Several structural/word measures move closer to upstream, while vocabulary
distribution moves slightly farther away. There is no uniform reduction in
the gap. Do not optimize these measurements independently of factual coverage.

## What this sample can show

The training outputs average about 259 words without the spec and 210–216
with it, versus 166 in the references. Both arms produce multi-paragraph
explanations, not one-liners. The longer sample exposes verbose walkthroughs,
unnecessary abstractions, unsupported explanations and omitted facts that the
initial sample could not adequately test.

Length is not quality. Reference counts include IR/example tokens, so lexical
and sentence measures are affected by the presence of code. An upstream
example can be more useful than a longer prose account. The model does not
receive the historical comment, so some omitted rationale may not be inferable
from code; a style prompt cannot reliably supply unavailable facts.

The judge is the same model as the generator and is not human-calibrated. It
sees randomized condition labels but also the upstream factual reference.
Upstream GVN wording received style deficits partly for awkward grammar;
that is not evidence of AI authorship. A “Claudishness” score here measures
the rubric's style judgment, not the probability that an AI wrote the text.
The judge varies across fresh calls, even in which reference omissions it
flags. All original grades and explanations remain available.

The upstream loop-traversal block says constant-foldable switches are future
work, although the visible code already handles them. Its meaning score is 2.
Historical human references are not infallible and must not be silently fixed
or copied as ground truth where the code contradicts them.

This is a deliberately selected 12-block, seven-file sample, not a random
survey of LLVM. The shared request for a substantial explanation and expanded
contexts may encourage overly broad walkthroughs. Both arms receive the same
task, but these findings need not transfer to normal code-editing tasks or
neutral prompts. No full generated comment exactly matches its reference
after whitespace normalization; this does not rule out partial memorization.
There are no human ratings or repeated draws. Do not pool these results with
the original short-comment series, whose task and sampled lengths differ.

## Artifacts, verification and usage

All calls used `codex exec`, `gpt-5.6-sol`, medium effort, and CLI 0.154.0.
The [artifact audit](audit.json) verified 48 distinct fresh sessions: 32
generators and 16 judges across 16 paired observations of 12 distinct cases.
Round 01's twelve calls finished before the pause; this continuation made
36 calls. No completed call was rerun merely to change its answer.

The audit checked completed status, model/effort, unique thread IDs, saved
input hashes, identical prompts between arms, empty baseline guidance,
treatment guidance matching the frozen spec, absence of complete reference
text from generation prompts, and freezing before validation/test. The
corpus loader and runner also enforce source/reference hashes, masking and
code preservation. Every run retains exact prompts, outputs, grades and
comment-only diffs.

Three focused long-corpus tests passed before the pause; the original 14-case
corpus was also checked after the loader change. This continuation rebuilt
the spec, validating its dictionary inputs, and audited saved artifacts. It
did not repeat unchanged tests or run smoke tests. No upstream writes or
checkpoint commits were made.

Saved usage totals for this long-block series: 541,955 input tokens, including
72,064 cached input tokens; 41,040 output tokens; and 23,916 separately reported
reasoning-output tokens. This continuation accounts for 405,284 input tokens,
including 45,952 cached, 30,324 output tokens, and 17,668 separately reported
reasoning-output tokens. These are raw CLI fields, not a billing estimate,
and exclude the conversation constructing the project.

No further calls or revisions are planned in this series. Future tuning that
uses these exposed test results must treat them as development data and use a
new holdout. The useful next evidence is real maintainer review of long blocks
and a task that supplies the intended documentation scope without leaking the
reference wording—not more attempts on the same exposed cases.
