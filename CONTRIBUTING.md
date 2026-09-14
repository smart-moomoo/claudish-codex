# Improving the comments

The four-criterion contract also covers text and code; see
[its scope](docs/change-scope.md). Shared invasiveness and optimality guidance
lives in `specs/changes-base.md`. The dictionary remains comment-specific.
Rebuild both generated guides with `python -m claudish build-spec` after
changing either source. Broader guidance changes need their own frozen
evaluation series; existing comment results do not validate them. Do not
change an evaluation rubric merely to improve the guide's scores.

The dictionary is an input to the Codex spec. `python -m claudish build-spec`
turns every accepted entry's guidance, example, and exceptions into
`specs/codex-comments.md`. Updating the dictionary without rebuilding the spec
fails CI. This connection addresses the ambiguity raised in
[the original project's issue #1](https://github.com/programasweights/claudish/issues/1).

1. Find a recurring problem in training outputs or a real Codex-generated diff.
   Include the exact output, relevant code context, model and effort, and a
   source link or experiment ID. A word alone is not evidence of bad prose.
2. Edit `dictionary/entries.json`: choose a stable ID and dimension; explain
   when the pattern is unhelpful; give a faithful synthetic before/after pair;
   include at least one legitimate exception. Link evidence to a committed file
   or a public URL; a path into a private run directory is rejected, because a
   reviewer has to be able to open it. Do not present a synthetic example as
   human writing or as an actual model quotation.
3. Run `python -m claudish build-spec`. The generated Markdown is part of the PR.
4. Run a fresh paired training ablation. Inspect changes in words, structure,
   simplicity, meaning and usefulness. Include failures as well as successes.
   Use the same model, effort, task, corpus, rubric, and repeat count in both
   conditions. Keep the previous artifacts. Never resume a session across arms.
5. Review the examples and submit the entry, generated spec and experiment
   report together. Maintainers choose whether to accept the rule. The judge
   provides evidence, not approval. The issue form is also suitable for people
   who do not want to edit JSON.

Only maintainers run validation and untouched test splits for a release. Once
test results influence a rule, those cases are development data. Add a new
holdout before making another generalization claim. Split by file; for a larger
corpus also group near-duplicate functions and comment families across files.

The initial LLVM references come from March 2020. To add references, supply an
immutable upstream revision, file, lines, license and evidence that the prose
is human-authored. Prefer pre-assistant history or an explicit contributor
attestation. Upstream acceptance alone does not prove human authorship. Keep
source text verbatim; never repair a reference with an LLM. For another stratum
at the pinned revision, create a new `corpus/<name>/sources.json` mapping file
paths to train/validation/test splits, plus `selection.json` with locations
and context windows. Run `prepare-corpus --corpus-dir corpus/<name>` to fetch
and freeze it, then review hashes. A different revision requires updating the
fetcher's pin and documenting that change; do not relabel old source. Preserve
existing frozen corpora and results. Check that enough code context is visible
and no copy of the hidden comment remains nearby. See
[the long-block corpus](corpus/long-blocks/README.md) for a concrete example.

Choose the comment-length stratum deliberately. Good one-liners are not
evidence about long explanatory blocks. For a long-block training ablation:

```sh
python -m claudish ablate --corpus-dir corpus/long-blocks \
  --task evaluation/long-block-task.md --split train --out runs/my-long-rule \
  --model gpt-5.6-sol --effort medium --jobs 2
```

The reference length filter is not an output word quota. Inspect whether
examples and paragraphs explain necessary interactions or merely add bulk.
Word and sentence metrics count IR/example tokens too; do not optimize them
without examining the text and factual coverage.

The evaluation rubric is independently versioned and must not change merely
to make a spec revision score better. A rubric change starts a new evaluation
series with fresh baselines. Human calibration records must contain actual
reviewer ratings; do not manufacture a human benchmark using an LLM.

Local deterministic validation is deliberately small:

```sh
python -m claudish build-spec --check
python -m claudish verify-corpus
python -m unittest discover -s tests
```

These commands make no model calls. CI uses no model credentials. Run model
experiments deliberately, not on arbitrary contributor pull requests.
