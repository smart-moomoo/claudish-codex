# Claudish Codex

Claudish Codex gives Codex instructions for writing direct code comments and
revising prose and code without losing meaning or required behavior. It also
provides a comment-diff grader, a mixed-change reviewer, and LLVM experiments
that compare fresh agents with and without the instructions.

The guides are experimental. This revision replaces avoidance rules with
direct-writing instructions, a meaning-preserving deletion test, and review
of whole documents. It has not yet been evaluated in a new LLVM ablation.
[What changed and why](docs/editorial-rebuild.md).

## Use the guide

Copy [specs/codex-changes.md](specs/codex-changes.md) into your project and add
this line to its existing AGENTS.md, adjusting the path:

```text
When writing or changing text, comments or code, read and follow specs/codex-changes.md.
```

For comment-only work, copy and name
[specs/codex-comments.md](specs/codex-comments.md) instead. Both generated files
are standalone: users need neither this package nor the dictionary.
Redistribute the guide after rebuilding it from changed sources.

The guidance asks for direct statements, preserves supported reasons and
certainty in both directions, and starts with the organization of the whole
document or implementation. A code refactor may change the implementation;
it must preserve required behavior.

## Review a change

Use Python 3.11+ and an authenticated Codex CLI. Run commands from this
directory; no Python dependencies are needed. Optional: `pip install -e .`
adds the `claudish` command. From elsewhere, put
`--root /path/to/claudish-codex` before the subcommand.

```sh
python -m claudish review-change --input change.json --out runs/change-review
python -m claudish grade-diff --diff comments.diff --base-dir /path/to/before-source --out runs/comment-review
```

`review-change` reviews typed before/after artifacts together; provide complete
documents when organization matters. `grade-diff` grades each added or changed
C/C++ comment in a comment-only diff against the source **before** the change.
Neither command modifies the source. Both make model calls through
`codex exec`, using **gpt-5.6-sol, medium reasoning** by default.
See the [input contract](docs/change-scope.md#input-format) and
[grading options and parser limits](docs/reviewing.md).

| Criterion | Comments / docstrings | Other text | Code |
| --- | --- | --- | --- |
| Cleanliness: direct wording and coherent explanation | Applies | Not applicable | Not applicable |
| Effectiveness: needed explanation and detail | Applies | Not applicable | Not applicable |
| Invasiveness: unnecessary scope and dependencies | Applies | Applies | Applies |
| Optimality: organization, placement and fit | Applies | Applies | Applies |

Meaning and correctness are requirements, not rewards for good style. Missing
context leaves a judgment unassessed. A review never proves that code works or
that a change is globally optimal. [Scope and limitations](docs/change-scope.md).

## What the experiments establish

**Comment style improved more reliably than usefulness.** The
[scaled study](experiments/scaled/README.md) evaluated a frozen ten-rule
candidate on 150 file-disjoint selected comments. On 74 unseen analyzable pairs,
it improved all four style deficits and modestly improved meaning; usefulness
was inconclusive, and comments remained substantially longer than upstream.
That candidate is now [archived](specs/archive/scaled-comments.md), not the
current guide.

**Long explanations still exposed meaning regressions.** The
[long-block study](experiments/long-blocks/README.md) used 12 intact LLVM blocks
of 102–263 words. Average style improved on eight unseen blocks, but meaning
regressed on two validation cases. The earlier
[short-comment study](experiments/README.md), whose references had 12–38 words,
did not establish held-out improvement: meaning tied and usefulness worsened
slightly. Good one-liners do not establish good long explanations.

**Good wording did not establish good placement or scope.** In the
[ladder study](experiments/ladder/README.md), 73 of 74 spec comments passed the
style screen, 23 of those passed effectiveness, and 7 passed all four criteria.
Meaning was reported separately, not used as a gate. The placement model
declined comments about as often as LLVM did, contradicting the study's
prediction. On 20 held-out commit tasks, generated changes overlapped the
upstream fix in 12 cases; 10 passed the shape ladder. Median changed lines
were 2 generated versus 3 upstream. These corrected shape measurements do
not establish correctness: the experiment did not compile or run LLVM.

The references are verbatim historical LLVM comments, not fabricated human
ratings. Their March 2020 provenance is not an individual authorship
attestation. Shared generator/judge bias and possible training-data
memorization remain limitations. Published results do not validate the new
guides or whole-document review contract.

[Run or resume an experiment](docs/experiments.md), including protocols,
isolation, saved evidence, and offline scoring. Raw model outputs and
downloaded sources stay local and are ignored by Git; public files contain
implementation, provenance, protocols and aggregate reports.

## Improve the guidance

Edit the maintained sources, then rebuild:

```sh
python -m claudish build-spec
```

Shared prose principles live in `specs/prose-base.md`; change scope and workflow
in `specs/changes-base.md`; comment guidance in `specs/base.md` and
`dictionary/entries.json`. Do not edit generated guides by hand.

Contributions need contextual examples, preserved facts and implications,
legitimate exceptions, and real evidence for claims of improvement. Keep the
judge fixed while tuning; use fresh holdouts after exposed test cases become
development data. See [CONTRIBUTING.md](CONTRIBUTING.md) for the issue/PR
workflow and focused checks. CI makes no model calls and uses no secrets.

Inspired by [programasweights/claudish](https://github.com/programasweights/claudish).
Original code is MIT licensed; LLVM source and derived excerpts retain their
own license. See [NOTICE.md](NOTICE.md).
