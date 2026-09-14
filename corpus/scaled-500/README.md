# 500-comment LLVM corpus

500 intact, standalone upstream comments from LLVM 10.0.0 at
`d32170dbd5b0d54436537b6b75beaf44324e0c28` (March 2020), selected
mechanically. The 128 source files are disjoint from all three earlier
corpora, so no previously inspected case reappears. Every reference is
extracted verbatim from hash-locked source. Historical provenance is not an
individual authorship attestation.

Splits are assigned by file, so no file contributes to more than one split.

| Split | Files | Cases | Short (20–49 words) | Medium (50–99) | Long (100–300) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 64 | 250 | 84 | 83 | 83 |
| Validation | 33 | 130 | 44 | 43 | 43 |
| Test | 31 | 120 | 40 | 40 | 40 |

Within every split and length band the selector held its intended mix of
functional classes: a fifth examples, the rest split evenly between rationales
and mechanism descriptions. Those labels come from lexical patterns in the
reference text. They balance sampling and are not semantic ground truth.

## Breadth

Earlier corpora drew only on Analysis, Transforms, CodeGen and Support. This
corpus spans sixteen subsystems; the earlier studies covered only the handful
of passes they sampled and could not support conclusions about LLVM beyond
them.

| Subsystem | Cases | Subsystem | Cases |
| --- | ---: | --- | ---: |
| CodeGen | 186 | ProfileData | 8 |
| Transforms | 126 | LTO | 6 |
| Analysis | 63 | Demangle | 4 |
| Support | 20 | ExecutionEngine | 4 |
| IR | 19 | Bitcode | 4 |
| MC | 19 | Linker | 4 |
| DebugInfo | 15 | TextAPI | 2 |
| Object | 12 | MCA | 8 |

## How the selection was frozen

Candidate files were drawn from every non-target library under `llvm/lib`
above 15 KB, excluding the 52 files touched by any earlier study. Before
selection, the comment scanner rejected 69 of 433 candidates, mostly for using
line splices. The remaining files were assigned to splits in
longest-comment-first order, so each split holds roughly twice the long-block
supply its quota needs.

`python -m claudish select-corpus --corpus-dir corpus/scaled-500 --train 250
--validation 130 --test 120 --seed 20260912` writes `selection.json` and
`selection-report.json`. Eligibility excludes banners, license headers,
generated-file markers, task markers such as TODO, blocks that are mostly
punctuation, trailing comments sharing a line with code, and any comment whose
own text already appears in the context window a generator would see. Within
each split the selector fills length bands longest first, caps any one file at
six cases, and orders candidates by a recorded SHA-256, so the result is
reproducible from the seed alone. No file reached the cap; the busiest
contributes four cases. The selector refuses to run when a selection already
exists, so a frozen corpus cannot be silently replaced.

`prepare-corpus --corpus-dir corpus/scaled-500` then fetches the pinned sources
and freezes each reference hash into `cases.json`. `verify-corpus --corpus-dir
corpus/scaled-500` checks source, license and reference integrity offline.

## Context windows

Each generator sees 45 lines before and 90 lines after the masked location,
with the reference replaced by a single `<COMMENT_TO_WRITE>` marker. The
reference, the rubric, the repository checkout and every other candidate stay
outside that window.

## Positions where a comment may not belong

`placement.json` freezes 60 positions in the training files: 30 where LLVM
wrote a comment and 30 where it wrote nothing. Both are shown the same way, as
a single `// <DECISION_POINT>` line with the same context window, so the model
decides rather than being told. An uncommented position is only used where
nothing is commented in the eight lines above it, so a class already explained
above its enclosing namespace is not counted as unexplained.

`python -m claudish select-placement --corpus-dir corpus/scaled-500
--per-split 60 --seed 20260913 --split train` rebuilds it. Positions are
ordered by a recorded hash and capped at three per file. Upstream's own choice
is the reference, and it is a weak one in the uncommented direction: LLVM
leaves plenty of places uncommented that could fairly carry a comment.
