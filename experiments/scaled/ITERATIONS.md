# Scaled iteration record

## Corpus freeze

The 150 locations and their train/validation/test file assignments were frozen
before generation. An invariant check rejected the first mechanical selection
because a reference sentence was duplicated in its context; the selector was
tightened before any model call. No outcome informed the replacement.

## Training round 1

The existing nine-rule candidate improved every mean deficit. Style bootstrap
intervals excluded zero; meaning improved by 0.147 and usefulness by 0.040.
Treatment comments still averaged 149 words versus 83 upstream. Eleven cases
had a higher treatment meaning deficit, although none regressed severely.

Inspection of those training cases showed repeated scope expansion: a local
marker prompted a function-wide explanation with unsupported rationale. Four
invalid judgments were preserved and excluded.

## Single revision and training round 2

Added `match-placement-scope`, which tells Codex to infer scope from placement
and default to the shortest form that preserves the local non-obvious fact.
The base guidance was updated consistently and the generated spec rebuilt.

The fresh 75-pair rerun again improved all mean deficits. Its style and meaning
intervals excluded zero; usefulness remained inconclusive. Treatment comments
averaged 144 words. Fourteen cases had localized meaning regressions, with none
severe. One invalid judgment was preserved. The ten-rule candidate was frozen
using training evidence only.

## Validation and test

Validation analyzed 39 of 40 pairs after preserving one delimiter-bearing
generation as invalid. Style improved; meaning and usefulness were essentially
tied, and there were no severe meaning regressions. No changes were made.

The untouched 35-case test improved all six mean deficits, with every bootstrap
interval below zero. Two cases had localized meaning regressions, neither
severe. The test split is now retired and must not guide future revisions.
