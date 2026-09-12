# Scaled LLVM comment corpus

150 intact, standalone upstream comments from LLVM 10.0.0 at
`d32170dbd5b0d54436537b6b75beaf44324e0c28` (March 2020), selected mechanically
rather than by hand. The 36 source files are disjoint from both the initial
short-comment corpus and the long-block corpus, so no previously inspected
case reappears. Every reference is extracted verbatim from hash-locked source.
Historical provenance is not an individual authorship attestation.

Splits are assigned by file, never by comment, so no file contributes to more
than one split.

| Split | Files | Cases | Short (20–49 words) | Medium (50–99) | Long (100–300) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 18 | 75 | 25 | 25 | 25 |
| Validation | 9 | 40 | 14 | 13 | 13 |
| Test | 9 | 35 | 12 | 12 | 11 |

Each case also carries a `functional_class` of example, rationale or mechanism.
Those labels come from lexical patterns in the reference text. They balance
sampling across kinds of comment and are not semantic ground truth; do not
report them as a classification result.

## How the selection was frozen

`python -m claudish select-corpus --corpus-dir corpus/scaled` walks every
eligible comment in the locked sources and writes `selection.json` plus
`selection-report.json`. Eligibility excludes banners, license headers,
generated-file markers, task markers such as TODO, blocks that are mostly
punctuation, trailing comments that share a line with code, and any comment
whose own text already appears in the context window a generator would see.
Within each split the selector fills length bands longest first, caps any one
file at six cases, and orders candidates by a recorded SHA-256 so the result is
reproducible from the seed alone. It refuses to run when a selection already
exists, so a frozen corpus cannot be silently replaced.

`prepare-corpus --corpus-dir corpus/scaled` then fetches the pinned sources and
freezes each reference hash into `cases.json`. `verify-corpus --corpus-dir
corpus/scaled` checks source, license and reference integrity offline.

An invariant check rejected the first mechanical selection because one
reference sentence was duplicated in its own context window. The selector was
tightened before any model call, and no outcome informed the replacement.

## Context windows

Each generator sees 45 lines before and 90 lines after the masked location,
with the reference replaced by a single `<COMMENT_TO_WRITE>` marker. The
reference, the rubric, the repository checkout and every other candidate stay
outside that window.
