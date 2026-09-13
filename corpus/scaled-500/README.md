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
one spans sixteen subsystems, which is the point: the earlier studies could not
speak to LLVM beyond the handful of passes they sampled.

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
above 15 KB, excluding the 52 files any earlier study had touched. Files the
comment scanner refuses, mostly those using line splices, were dropped before
any selection; 69 of 433 candidates fell out that way. Files were then dealt to
splits longest-comment-first, so each split holds roughly twice the long-block
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
