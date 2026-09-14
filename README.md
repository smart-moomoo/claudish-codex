# Claudish Codex

Guide Codex changes to text, comments and code. Cleanliness and effectiveness
apply to comments; invasiveness and optimality apply to all three. The existing
LLVM experiments measure comments and limited code-change proxies against
historical upstream material. They do not yet validate the broader guidance.

The project contains a [general-change spec](specs/codex-changes.md), the
original [comment-only spec](specs/codex-comments.md), a
[dictionary](dictionary/entries.json) that generates the comment guidance,
a C/C++ diff grader, and a reproducible LLVM ablation runner. All model calls
use `codex exec`; defaults are **gpt-5.6-sol, medium reasoning** for both the
generator and the judge. There is no API SDK dependency or substitute model.

The [completed initial LLVM study](experiments/README.md) includes three
training rounds, validation, and held-out evaluation. The held-out results
did **not** establish an improvement: meaning scores tied and usefulness was
slightly worse with the spec. The spec remains experimental; aggregate evidence
and iteration notes include regressions, while detailed runs stay local.

The initial references were only 12–38 words. A separate
[long-block study](experiments/long-blocks/README.md) resamples 12 intact LLVM
blocks of 102–263 words to examine explanations beyond one-liners. It is now
complete: the revised spec improved average style on eight unseen blocks,
but meaning regressed on two validation cases. It remains experimental.
Three full-length contrasts, including a regression, remain in the private
local experiment artifacts.

A separate [ladder study](experiments/ladder/README.md) asks four questions in
increasing order of difficulty: is the comment well written, does it belong
there at that length, is it the smallest thing that works, and is it right for
the whole file. The first step is where almost everything is lost. On 74 unseen
pairs, 73 of 74 comments written with the spec read well, 23 of those are the
right length and explain the right thing, and 7 clear all four. These are style
and scope criteria; meaning is reported separately, not used as a gate. Asked whether a
comment belongs at a position at all, the model declines about as often as LLVM
did, which contradicts the study's own written prediction. Given the files
before a real commit from a corpus of
[40 LLVM changes](corpus/commits/README.md), it finds the area the real fix
touched in 12 of 20 cases. The median is 2 changed lines against 3 upstream;
10 of 20 clear the shape ladder. These corrected measurements replace an
earlier analysis that incorrectly counted unchanged edit anchors.

The [scaled LLVM study](experiments/scaled/README.md) expands this to 150
file-disjoint, length- and function-stratified comments with two fresh judges
per pair. The frozen ten-rule candidate improved all four style deficits on 74
unseen analyzable pairs and modestly improved meaning; usefulness was
inconclusive. It passed the advisory screen, while remaining substantially more
verbose than the historical upstream comments. The comment-only spec is this
scaled candidate; the earlier studies evaluated prior versions. The broader
change spec adds new, not yet empirically validated guidance.

Raw experiment directories and downloaded LLVM files are private local
artifacts by default and are excluded from Git. The repository publishes the
implementation, immutable source/reference manifests, protocols, aggregate
results, and iteration notes. Run `prepare-corpus` to recreate the pinned
source trees, and run fresh experiments to produce local detailed artifacts.

## Use the spec

Copy `specs/codex-changes.md` into your repository, then add this instruction
to its existing `AGENTS.md`, adjusting the path:

```text
When writing or changing text, comments or code, read and follow specs/codex-changes.md.
```

Merge this instruction with your existing guidance. The generated spec is
standalone; it does not need this project's Python package or dictionary at
runtime. Rebuild and redistribute it when the dictionary changes.

| Criterion | Comments / docstrings | Other text | Code |
| --- | --- | --- | --- |
| Cleanliness | Applies | Not applicable | Not applicable |
| Effectiveness | Applies | Not applicable | Not applicable |
| Invasiveness | Applies | Applies | Applies |
| Optimality | Applies | Applies | Applies |

Code refactoring may change implementation while preserving required behavior.
A small diff is not sufficient if it omits required work. Optimality means
justified placement and fit in the supplied context, not a globally best
solution. Correctness and task completion remain requirements for every kind.

Use `specs/codex-comments.md` for comment-only work and existing frozen LLVM
ablations. Its contents and the historical rubrics/results are unchanged.
The [scope and review guide](docs/change-scope.md) distinguishes the broader
contract from the earlier experimental proxies.

## Run the tools

Requirements: Python 3.11+ and an authenticated
[Codex CLI](https://learn.chatgpt.com/docs/non-interactive-mode).
Run these commands from this project's directory. No Python dependencies are
needed; `python -m claudish` works directly. Optional: `pip install -e .` adds
the `claudish` command. Use `--root /path/to/claudish-codex` before the subcommand
when invoking it from elsewhere.

Review a mixed-content change with explicit artifact types:

```sh
python -m claudish review-change --input change.json --out runs/change-review
```

This sends the task, before/after artifacts and their context to one fresh
judge using a separately versioned rubric. It never edits source files or
executes the submitted code. See the [input format](docs/change-scope.md#input-format).
The first two criteria are reported as not applicable for text/code; missing
context is unassessed, never a pass. This command makes one model call, unlike
an offline check or the historical commit-shape scorer.

Grade a comment-only diff against the source tree **before** the change:

```sh
python -m claudish grade-diff \
  --diff comments.diff --base-dir /path/to/before-source --out runs/review
```

Every added or changed comment receives a location, six 0–4 grades, evidence,
an explanation, missing facts, and unsupported claims in `grades.json`.
Zero is best; four is a severe problem. The dimensions are Claudishness,
words, structure, simplicity, meaning, and usefulness. A multiline comment is
graded as a whole even when only one line changes. Removed comments are
counted as touched old comments; no replacement text is invented. Attribution
to Codex comes from the caller, since a diff cannot establish authorship.

`--extract-only` saves extracted comments without invoking a model. `--diff -`
reads stdin. Executable token changes and preprocessor changes are rejected.
The grader supports ordinary unified diffs over existing C/C++ files. It
requires matching base content and rejects unsupported paths, binary patches,
combined diffs, renames, line splices and trigraphs. This is a lexical scanner,
not a compiler or a general-language comment parser. It never applies changes
to the supplied source directory.

Run a paired LLVM experiment:

```sh
python -m claudish ablate --split train --out runs/my-revision \
  --model gpt-5.6-sol --effort medium --jobs 2
```

The vendored historical corpus is ready to use. `prepare-corpus` can fetch
missing source files from the pinned commit; existing files must match their
hashes. `verify-corpus` checks source and reference integrity offline.

Use the long-block stratum and its shared explanatory task with:

```sh
python -m claudish ablate --corpus-dir corpus/long-blocks \
  --task evaluation/long-block-task.md --split train --out runs/long-revision \
  --model gpt-5.6-sol --effort medium --jobs 2
```

`prepare-corpus` and `verify-corpus` also accept `--corpus-dir`.
`ablate --rubric path/to/rubric.md` selects a separate fixed judge series;
do not change the rubric while iterating on a spec. Custom corpus, task and
rubric paths are relative to `--root` unless absolute. Existing corpus and run
directories are preserved. See the [resampling protocol](experiments/long-blocks/PROTOCOL.md).

Each arm gets the same excerpt with one comment hidden. Every case, arm,
repeat and judge uses a new ephemeral Codex session in a temporary working
directory and Codex home. Only authentication is copied into that home;
personal settings, instructions, skills, memories and previous answers are
excluded. The treatment AGENTS.md adds the spec. Baseline AGENTS.md contains
only the common task/output instruction. No checkout, original comment or
judge rubric is exposed to the generator. Tools are disabled and unexpected
tool use invalidates the call.

Model access is needed for experiments and grading. The runner uses your
existing Codex login or the CLI's supported environment authentication. It
records prompts, guidance, model/effort, CLI version, thread IDs, timing and
token usage. Credentials stay in the temporary home and are never copied into
reports. Runs make no upstream writes, commits, PRs or messages.

Each run saves:

- `report.md`, `summary.json`, and `results.json`: paired grades, descriptive
  measurements, and side-by-side upstream/baseline/treatment comments.
- `calls/`: exact generation and judge prompts, schemas, answers, events,
  metadata, and a comment-only diff for each generated comment.
- `manifest.json`, `spec.md`, `dictionary.json`, `rubric.md`, `cases.json`:
  the inputs and hashes needed to inspect the experiment.
- New runs also snapshot `task.md` and `sources.lock.json`, including custom
  corpus/task choices. Long-block measurements add paragraph count,
  words per paragraph and maximum sentence length; old results are unchanged.

Output directories must be new. Failures remain visible and never become
passing results. Do not selectively reroll bad comments. Increase `--repeats`
for more evidence and `--timeout` for slower calls. The seed controls task
interleaving and anonymous labels, not model sampling.

A model answer that breaks the prose contract is excluded from its run and
recorded in `excluded_generation_pairs`; it is never rerolled. `--judges 2`
requests two independently randomized fresh judgments per pair. A judgment that
violates the response schema is preserved with its raw answer and excluded from
the scores.

`select-corpus` deterministically freezes a scaled, file-disjoint selection from
a prepared source manifest. `resume-run --run runs/my-revision` continues a run
that was interrupted or failed: every completed call is reused from its saved
answer, and only the calls that never finished are made again. Stopping a long
run therefore costs nothing already paid for. Resuming refuses a run whose
spec, rubric, task or corpus no longer matches its manifest, so a resumed run
cannot mix inputs.

Two commands make no model requests. `reaggregate --run runs/my-revision`
rebuilds a run's summary and report from its saved rows, so a repaired
aggregation or validator can be applied to stored responses without new calls
and without editing a score; a preserved judgment that becomes valid is
recovered and counted in `recovered_judgments`. `aggregate` combines finished
runs into one published result:

```sh
python -m claudish aggregate --out experiments/scaled/results.json \
  --run training_round_1=experiments/scaled/train-01 \
  --run training_round_2=experiments/scaled/train-02 \
  --run validation=experiments/scaled/validation \
  --run test=experiments/scaled/test \
  --combine combined_unseen=validation,test
```

Pooled rows keep the order of the labels given, which fixes the bootstrap draws.

## Four criteria, hardest last

The judge rubric asks whether a comment is well written. Three further
questions it cannot reach are whether a comment belongs at that location and
at that length, whether it is the smallest thing that does the job, and
whether it is right for the file rather than only for its own line. Those are
scored in order, each only for the cases that passed the one before, and the
[ladder study](experiments/ladder/README.md) reports how far comments get.

Two of the commands make no model requests:

```sh
python -m claudish score-tiers --run runs/a --run label=runs/b --out ladder.json
python -m claudish measure-generations --run runs/a
```

`score-tiers` scores finished runs and pools several into one ladder.
`measure-generations` works on a run that was stopped before judging: it
reports the length and coupling of every saved comment, including how closely
length follows the location.

The other three need model calls:

```sh
python -m claudish placement-run --split train --corpus-dir corpus/scaled-500 --out runs/placement
python -m claudish judge-files --run runs/a
python -m claudish commit-run --split train --corpus-dir corpus/commits --out runs/patches
```

`placement-run` asks whether a comment belongs at each of the 60 frozen
positions in `corpus/scaled-500/placement.json`, half of which LLVM left
uncommented; the model may decline. `judge-files` judges each file's comments
as a set against [a second rubric](evaluation/file-rubric.md), which is where
repetition across a file becomes visible. `commit-run` gives fresh agents the
files as they stood before a real LLVM commit and that commit's message, and
compares the edits it gets back with what upstream actually did. Placement is
always paired, using the generated comment spec unless `--spec` overrides it.
`commit-run` has a single arm unless `--spec` supplies code-writing guidance.
All three accept `--resume` only with matching saved inputs, model and effort.
Failed attempts are archived, not deleted. Legacy placement/commit manifests
without input fingerprints cannot be resumed; use a new output directory.

File judging now writes `file-calls-v2/` and `file-judgments-v2.json`, leaving
the old leaked-context series intact. `score-tiers` ignores old file judgments
and checks the new judgments against the run's rows and corpus. Invalid judge
responses are preserved and excluded, never rerolled.

Commit scoring compares original and final sources, not replacement anchor
sizes. Existing commit answers can be rescored without model calls or changing
the original run:

```sh
python -m claudish rescore-commits --run runs/patches --out runs/patches-rescored
```

Nothing in the commit study compiles or runs LLVM, so none of it says whether
a generated change is correct. It measures what a change touches and where.
An answer that changes nothing would look ideal on both, so an answer counts
only when every edit applies and it overlaps the real commit at all.

## Evidence and limits

Read [the study summary](experiments/README.md), [initial protocol](experiments/PROTOCOL.md), and
[iteration notes](experiments/ITERATIONS.md). The initial corpus contains 14
comment locations across four files from LLVM 10.0.0 (March 2020): six training,
four validation, four test. Splits are by file. References are verbatim
upstream comments with immutable source links and SHA-256 hashes. This history
predates modern code assistants; it is not an individual authorship attestation.

The judge sees anonymous candidates and a fixed rubric, never the evolving
dictionary or spec. It also receives the upstream comment as a factual
reference, so it can recognize that candidate's text. This is condition-blind
comparison, not a fully blind comparison to the reference. The same model
family generates and judges, which can introduce shared bias. No human judge
calibration has been claimed or fabricated.

Style scores are subjective and need human calibration. Word count, sentence
length, vocabulary, compounds, repetition and lexical distance are descriptive
measurements, not automatic quality targets. Technical terminology is allowed.
Shortening a comment is a regression if it removes an important fact.
Reconstructing comments can expose missing historical rationale, and the
model may have memorized LLVM during pretraining. These small experiments do
not establish performance across all LLVM projects or comment styles.

## Improve the dictionary

```sh
# Edit dictionary/entries.json, then:
python -m claudish build-spec
python -m claudish ablate --split train --out runs/new-dictionary
```

Every entry needs a contextual rule, faithful synthetic before/after example,
and legitimate exceptions. Accepted entries directly change the generated
spec. Link real failures and the resulting ablation. Keep the judge fixed
while tuning. Compare meaning and usefulness as well as style. Use validation
after training; evaluate the test split only after freezing a choice. Exposed
test cases become development data for future iterations.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the issue/PR workflow and targeted
offline checks. CI verifies dictionary/spec synchronization, source/reference
hashes, and the parser/judge contracts. CI does not call models or use secrets.

Inspired by [programasweights/claudish](https://github.com/programasweights/claudish).
Original code is MIT licensed; LLVM source and derived excerpts retain their
own license. See [NOTICE.md](NOTICE.md).
