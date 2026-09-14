# 40 small LLVM commits

This corpus compares generated edits with real LLVM commits to measure what a
change touches and whether it is in the right place. The model receives the
files as they stood before a commit and that commit's own message, then returns
edits. The commit is the reference.

Selected mechanically from the 700 commits reachable from
`d32170dbd5b0d54436537b6b75beaf44324e0c28` (March 2020), the same pin the
comment corpora use, so the sources predate modern code assistants. 532 of
those were rejected, most for touching files outside the LLVM libraries or for
a message too short to act on. Historical provenance is not an authorship
attestation.

| Split | Commits |
| --- | ---: |
| Train | 20 |
| Validation | 8 |
| Test | 12 |

Splits follow the file path, so no file appears in two splits. 38 distinct
files across 40 commits; 37 commits touch one file and 3 touch two. Changed
lines run from 4 to 60, median 11. 11 commits touch a header. The pre-change
sources total 2.3 MB, between 6 KB and 179 KB per case.

| Subsystem | Files | Subsystem | Files |
| --- | ---: | --- | ---: |
| Target | 16 | IR | 3 |
| Transforms | 10 | DebugInfo | 2 |
| CodeGen | 6 | ADT | 2 |
| Support | 3 | Analysis | 1 |

## What a commit had to be

One parent. C++ under `llvm/lib` or `llvm/include/llvm`. At most three files
and 4 to 60 changed lines, so the change is small enough to attempt and large
enough to have a shape. No added, deleted, renamed or binary files. Not a
revert or a recommit. A message of at least eight words, since the message is
the instruction. Pre-change sources under 200 KB in total, so they can all be
supplied. All files in one split.

`python -m claudish select-commits --corpus-dir corpus/commits --count 40
--scan 700 --seed 20260913` walks history, applies those rules in order and
freezes what it accepts into `commits.lock.json` with a hash for every patch
and every pre-change file. It refuses to run when a selection already exists.

`prepare-commits --corpus-dir corpus/commits` refetches the patches and
sources from the lock and checks every hash; `verify-commits` checks them
offline. The lock is published, the sources and patches are not.

## What is measured, and what is not

Nothing here compiles or runs LLVM, so the measurements do not establish
whether a change is correct. They cover files touched, lines changed, headers
touched that the real change left alone, symbols introduced that the pre-change
sources did not have, and how much the answer's changed lines overlap the real
commit's.

An answer that changes nothing would score perfectly on all of those, so an
answer counts only if every edit applies to the supplied sources and it
overlaps the real change at all. The model is told which files are in play,
which makes the count of files touched weak; the line-level overlap is the
measure that carries weight.
