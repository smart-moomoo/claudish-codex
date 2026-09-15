# Running experiments

Run commands from the project root with Python 3.11+ and an authenticated
Codex CLI. All model calls use `codex exec`, `gpt-5.6-sol`, medium reasoning.
Detailed outputs stay local; do not publish raw runs or downloaded LLVM files.

## Choose the candidate and split

The current guides are a new editorial candidate, not the spec evaluated in
the published studies. Tune on training data only. Freeze the candidate and
judge rubric before validation or test; once a test informs a choice, retire
it as a holdout. Do not reuse published test cases as fresh holdouts for the
rebuilt guide.

For the historical scaled candidate, pass
`--spec specs/archive/scaled-comments.md` to `ablate` or `placement-run`.
Its archived sources and hashes are in [the archive](../specs/archive/README.md).
Use the study's original corpus, task, rubric and settings from its protocol;
fresh model outputs are new evidence, not a reproduction of saved answers.
With a custom `--spec`, the runner still snapshots the current repository
dictionary as metadata; it does not rebuild that spec from the snapshot.
Consult the archived dictionary for the historical guide's source entries.

## Prepare and run

Fetch the pinned sources with `python -m claudish prepare-corpus` and check them
offline with `python -m claudish verify-corpus`. Downloaded sources stay local.

Run a paired LLVM experiment:

```sh
python -m claudish ablate --split train --out runs/my-revision \
  --model gpt-5.6-sol --effort medium --jobs 2
```

`prepare-corpus` fetches missing source files from the pinned commit; existing
files must match their hashes. Use the same prepared corpus for both arms.

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
directories are preserved. See the [resampling protocol](../experiments/long-blocks/PROTOCOL.md).

## Isolation and saved evidence

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

## Resume or recompute

`select-corpus` deterministically freezes a scaled, file-disjoint selection from
a prepared source manifest. `resume-run --run runs/my-revision` continues a run
that was interrupted or failed: saved, completed calls are reused,
so stopping does not make you pay for that work again. Calls without a saved
answer may run again. Resuming refuses a run whose
spec, rubric, task or corpus no longer matches its manifest, so a resumed run
cannot mix inputs.

Two commands make no model requests. `reaggregate --run runs/my-revision`
rebuilds a run's summary and report from its saved rows, so a repaired
aggregation or validator can be applied to stored responses without new calls
and without editing a score; a preserved judgment that becomes valid is
recovered and counted in `recovered_judgments`. `aggregate` combines finished
runs into one published result:

```sh
python -m claudish aggregate --out runs/combined-results.json \
  --run training_round_1=runs/scaled/train-01 \
  --run training_round_2=runs/scaled/train-02 \
  --run validation=runs/scaled/validation \
  --run test=runs/scaled/test \
  --combine combined_unseen=validation,test
```

Pooled rows keep the order of the labels given, which fixes the bootstrap draws.

## Placement, file fit and code changes

The judge rubric asks whether a comment is well written. Three further
questions it cannot reach are whether a comment belongs at that location and
at that length, whether it is the smallest thing that does the job, and
whether it is right for the file rather than only for its own line. Those are
scored in order, each only for the cases that passed the one before, and the
[ladder study](../experiments/ladder/README.md) reports how far comments get.

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
as a set against [a second rubric](../evaluation/file-rubric.md), which is where
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

Read [the study summary](../experiments/README.md), [initial protocol](../experiments/PROTOCOL.md), and
[iteration notes](../experiments/ITERATIONS.md). The initial corpus contains 14
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
