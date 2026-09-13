# Scaled LLVM study protocol

Recorded before scaled-corpus generation. No model output informed this design.

## Corpus

Use 150 intact, standalone comments from LLVM 10.0.0 at commit
`d32170dbd5b0d54436537b6b75beaf44324e0c28`. The files in
`corpus/scaled/sources.json` do not occur in either earlier experiment. Assign
files, rather than individual comments, to immutable splits: 75 training, 40
validation and 35 test cases. Previously inspected validation and test cases
are retired and are not reused.

Stratify each split across short (20–49 words), medium (50–99 words), and long
(100–300 words) comments. Also label comments deterministically as examples,
rationales, or mechanism descriptions from lexical features. This label is a
sampling aid, not ground truth. Cap selection at six comments per source file
and use a recorded SHA-256 ordering inside each stratum. Exclude banners,
generated-comment markers, and blocks dominated by punctuation. References
are verbatim historical upstream comments; their provenance is not an
individual human-authorship attestation.

## Calls and isolation

For each case, generate one baseline and one treatment comment in separate,
fresh `codex exec` sessions. Use `gpt-5.6-sol`, medium reasoning, the existing
isolated temporary environment, and at most eight concurrent calls. Neither
generator sees the reference, judge rubric, other outputs, repository checkout,
personal instructions, memories, skills, or tools.

Judge each completed pair twice in separate fresh sessions. Randomize anonymous
candidate labels independently for the two judgments. Judges receive the fixed
`evaluation/rubric.md`, masked code context, all three anonymous comments, and
the upstream text as factual reference. They do not receive the spec or
dictionary. Preserve disagreements and regressions; do not selectively reroll.

## Iteration and analysis

Run the existing nine-rule spec on training first. Inspect aggregate and
failure-cluster evidence only from training. Permit at most one spec revision,
derived only from those failures, followed by a complete fresh training run.
Freeze the choice before validation. Validation may reject the candidate but
must not change it. Run the untouched test split once after that decision; it
then becomes retired holdout data.

Primary outcomes are paired changes in the six fixed judge deficits. Average
the two judge scores per generated comment, retain inter-judge disagreement,
and report deterministic case-level bootstrap 95% confidence intervals for
mean paired changes. Also report win/tie/loss counts, factual regressions,
comment length/structure measures, functional and length strata, call counts,
and token usage. Confidence intervals quantify sampling uncertainty within
this constructed corpus; they do not establish population validity or human
agreement.

The advisory screen requires a style improvement, no increase in mean meaning
or usefulness deficit, and no severe per-case meaning regression. Promotion
still requires review of full comments. No smoke tests, intermediate approval
stops, LLVM submissions, or test-driven tuning are allowed.
