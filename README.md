# Claudish Codex

Write useful, plain-English code comments with Codex. Measure the difference
with fresh agents on LLVM, using actual historical upstream comments as
references. Improve the spec through reviewed dictionary contributions.

The project contains a usable [Codex spec](specs/codex-comments.md), a
[dictionary](dictionary/entries.json) that directly generates its guidance,
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

The [scaled LLVM study](experiments/scaled/README.md) expands this to 150
file-disjoint, length- and function-stratified comments with two fresh judges
per pair. The frozen ten-rule candidate improved all four style deficits on 74
unseen analyzable pairs and modestly improved meaning; usefulness was
inconclusive. It passed the advisory screen, while remaining substantially more
verbose than the historical upstream comments. The current spec is this scaled
candidate; the earlier studies evaluated prior versions.

Raw experiment directories and downloaded LLVM files are private local
artifacts by default and are excluded from Git. The repository publishes the
implementation, immutable source/reference manifests, protocols, aggregate
results, and iteration notes. Run `prepare-corpus` to recreate the pinned
source trees, and run fresh experiments to produce local detailed artifacts.

## Use the spec

Copy `specs/codex-comments.md` into your repository, then add this instruction
to its existing `AGENTS.md`, adjusting the path:

```text
When writing or changing code comments, read and follow specs/codex-comments.md.
```

Merge this instruction with your existing guidance. The generated spec is
standalone; it does not need this project's Python package or dictionary at
runtime. Rebuild and redistribute it when the dictionary changes.

## Run the tools

Requirements: Python 3.11+ and an authenticated
[Codex CLI](https://learn.chatgpt.com/docs/non-interactive-mode).
Run these commands from this project's directory. No Python dependencies are
needed; `python -m claudish` works directly. Optional: `pip install -e .` adds
the `claudish` command. Use `--root /path/to/claudish-codex` before the subcommand
when invoking it from elsewhere.

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
passing results. `replay --run runs/my-revision` rebuilds reports from complete
saved calls without any model requests. It does not resume an agent. Incomplete
calls require a new run; do not selectively reroll bad comments. Increase
`--repeats` for more evidence and `--timeout` for slower calls. The seed controls
task interleaving and anonymous labels, not model sampling.

`--judges 2` requests two independently randomized fresh judgments per pair.
`select-corpus` deterministically freezes a scaled, file-disjoint selection
from a prepared source manifest. If every generation call completed but a
generated comment failed the prose contract before judging began, `resume-run`
can judge the remaining valid pairs without rerunning generations; exclusions
remain explicit in the aggregate result.

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
