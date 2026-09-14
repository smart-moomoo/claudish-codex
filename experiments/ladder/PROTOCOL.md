# Four criteria, hardest last

Recorded before any model call in this series. The re-analysis of finished runs
described under "What is already settled" is not preregistered and says so.

## The criteria

A collaborator proposed that comment and code quality be judged on four things,
and that they get harder in that order:

1. **Clean** — is it well written. The six existing judge scores cover this.
2. **Effective** — does a comment belong here, and should it be short or long.
3. **Invasive** — is it the smallest thing that does the job, and does it avoid
   depending on components it does not own.
4. **Optimal** — is it right for the file and the codebase, not only on its own.

Invasive and optimal are properties of a change. A comment is not a change, so
those two are also measured on generated code, using real LLVM commits.

A criterion is scored only for cases that passed the one before it, and the
highest criterion reached is reported. Truthfulness is not a rung: a comment
that misstates the code has failed at something more basic, so the judge's
meaning score sits beside the ladder rather than inside it.

## Bars

No bar is a number chosen for this study. Where the judge rubric grades a
dimension, the bar is the rubric's own wording: 2 is "noticeable", so passing
means staying under 2. Where no rubric exists, the bar is the upstream comment
written at the same location. The one exception is stated where it occurs: how
much a generated change must overlap the real commit to count as being in the
right place. Every raw measurement is recorded, so any other bar can be applied
later without a model call.

## What is already settled

The ladder was applied to the four finished runs of the 150-comment study, 224
analyzable pairs. Those runs were made and inspected before these criteria
existed, so this is a re-analysis and not a test of a prediction. It is
reported as such. The same applies to the length measurements taken from the
500-comment training generations.

## Effective: placement

60 frozen positions in the 500-comment corpus's training files, half where LLVM
wrote a comment and half where it wrote nothing. Both kinds are presented the
same way: one marker on its own line, the same context window, no other
difference the model can see. An uncommented position is only chosen where
nothing is commented in the eight lines above it, so a location already
explained just above does not count as unexplained.

Each position is answered once per arm in a fresh isolated session. The model
may decline. Agreement with upstream is the measure, split by what upstream did,
because upstream silence is weaker evidence than an upstream comment.

The hypothesis, written before running: the model asks for a comment at nearly
every position in both arms, and the difference between its rate at commented
and uncommented positions is small. If that is wrong, and it does discriminate,
that is the more interesting outcome and is reported as prominently.

## Optimal: a file's comments together

Every file in a finished run with three or more analyzable comments is judged
once, with all of that file's comments presented as a set, one set per arm plus
upstream, anonymously labelled. Three deficits on the existing 0–4 scale:
repetition across locations, comments that disagree with each other, and
explanation that went where it was not needed instead of where it was.
Individual wording is not re-judged.

## Invasive and optimal: real commits

40 commits reachable from the pinned LLVM commit, frozen in `corpus/commits`:
single parent, C++ under `llvm/lib` or `llvm/include/llvm`, at most three
files, 4 to 60 changed lines, no added, deleted, renamed or binary files, not a
revert, a message of at least eight words, and pre-change sources under 200 KB
in total. Splits follow the file path, so no file appears in two splits.

The model receives the whole pre-change files and the commit's own message, and
returns replacement edits. It is told which files are in play, which makes the
count of files touched a weak measure; the line-level comparison is the real
one. Nothing is compiled or tested, so nothing here says a change is correct.

Against the real commit: files touched, lines changed, headers touched that the
real change left alone, and symbols introduced that the pre-change sources did
not have. Placement is the overlap between the lines the answer touched and the
lines the commit touched.

An answer that does nothing would look perfectly uninvasive, so two things are
required before any shape measure counts: every edit applies to the supplied
sources, and the answer overlaps the real change at all. **The chosen number in
this design** is the overlap needed to count as the right place, set at 0.5
before running. The raw overlap is recorded for every case.

The comment spec is not guidance for writing code. A commit run therefore has
one arm unless guidance is deliberately supplied, in which case it becomes a
paired ablation like the others.

## Order and limits

Placement first, then the file-level judgments on the existing 150-comment
runs, then commits. Training splits first, test splits retired once read.

These measure what a comment says and what a change touches. They do not
establish human agreement, correctness of generated code, performance on code
written after the model's training data, or behaviour in a live editing
session. No smoke tests, no intermediate approval stops, no tuning against
these results.

## Implementation correction, 2026-09-13

This amendment was added after inspecting the first series and correcting
implementation errors. The original protocol above is retained; this is not
a new preregistration or a fresh holdout. No spec, dictionary, rubric or
threshold was tuned from these results.

The original file judge's shared context started at the reference comment,
not after it. All 17 original calls are invalidated for that comparison.
Version 2 starts at the parsed comment end, masks all comments in shared
source context and supplies the next six non-empty code lines. Seventeen
fresh isolated calls use the same rubric, label seed, gpt-5.6-sol and medium
effort. One response has evidence outside its assigned set; it is preserved
and excluded, not retried. Old and new raw artifacts remain local in separate
directories. Missing judgments are unmeasured, not failures.

Commit scoring originally counted old_text anchors, including unchanged
context, and interpreted offsets from later edits against the original file.
Version 2 applies all edits first, and applies the upstream patch to its
verified pre-change source. Both final files use the same line-based
SequenceMatcher with autojunk disabled. Changed original lines are counted;
a pure insertion is anchored to the preceding original line (line 1 at the
start). These are unique touched positions, not added-plus-deleted line
counts. Edits with no net change fail the applicability floor. All 20 saved
answers are rescored without new model calls, keeping the original run intact.

Resume now checks input fingerprints and saved call inputs before reusing an
answer. File-series fingerprints include the label seed, rubric, model,
effort, rows and corpus. Failed attempts are archived. Legacy ladder manifests
without complete fingerprints cannot be resumed. Aggregate v1 results are
retained under `superseded-v1/` solely as an audit trail.
