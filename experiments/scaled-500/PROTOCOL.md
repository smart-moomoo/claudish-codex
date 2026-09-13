# 500-comment LLVM study protocol

Recorded before any model call in this series. No output from this corpus
informed this design.

## What this study is

A replication, not a tuning round. The candidate is the existing frozen
ten-rule spec exactly as the 150-comment study left it. No dictionary entry,
spec text, task or rubric may change because of anything measured here. If the
result contradicts the earlier one, the contradiction is recorded and the spec
stays as it is until a separate, deliberately designed iteration.

The earlier study's stated limitation was its narrowness: 74 unseen comments
drawn from four LLVM subsystems, with a judge and generator sharing a model
family and a corpus old enough to be memorized. This study addresses only the
first of those. It cannot address the other two.

## Hypothesis, written before running

On 250 unseen comments spanning sixteen subsystems, the frozen candidate will
reproduce the direction of the four style improvements it showed on 74 unseen
comments, with bootstrap intervals excluding zero. Meaning is expected to
improve slightly or tie. Usefulness was inconclusive before and is expected to
remain inconclusive at this sample size. Treatment comments are expected to stay
substantially longer than the historical references.

A failure to reproduce the style result is the outcome that would matter most,
and it is recorded as prominently as a success.

## Corpus

500 comments at commit `d32170dbd5b0d54436537b6b75beaf44324e0c28`, frozen in
`corpus/scaled-500` before this protocol was written. Splits are assigned by
file: 250 train, 130 validation, 120 test. No file appears in more than one
split, and no file appears in any earlier corpus. Each split holds equal thirds
of short, medium and long references. Selection, strata and eligibility rules
are described in the corpus README and are not revisited here.

## Calls and isolation

For each case, one baseline and one treatment comment in separate fresh
`codex exec` sessions, `gpt-5.6-sol`, medium reasoning, the existing isolated
temporary environment, at most eight concurrent calls. Neither generator sees
the reference, the rubric, other outputs, the checkout, personal instructions,
memories, skills or tools.

Each completed pair is judged twice in separate fresh sessions with
independently randomized anonymous labels. Judges receive the fixed
`evaluation/rubric.md`, the masked context, all three anonymous comments and the
upstream text as factual reference. They never see the spec or dictionary.

A generation that breaks the prose contract excludes its pair and is recorded.
A judgment that breaks the response schema is preserved with its raw answer and
excluded from the scores. Nothing is rerolled, and no bad comment is replaced.

## Order

Train, then validation, then test, run and reported in that order. Training is
run first as additional paired evidence and as the reserve for any future
tuning round; it does not change the candidate in this study. The test split is
retired once its result is known.

## Analysis

Primary outcomes are paired changes in the six fixed judge deficits, averaging
the two judgments per comment and retaining their disagreement. Report
deterministic case-level bootstrap 95% intervals, win/tie/loss counts, meaning
regressions and severe meaning regressions, comment length and structure
measures, and breakdowns by length band, functional class and subsystem.

The advisory screen is unchanged: a style improvement, no increase in mean
meaning or usefulness deficit, and no severe per-case meaning regression. It
remains advisory and promotes nothing by itself.

Intervals describe case-level sampling uncertainty inside this constructed
corpus. They do not establish human agreement, nor performance on code written
after the model's training data, nor performance in a live editing workflow.
No smoke tests, intermediate approval stops, upstream submissions, or
test-driven tuning.
