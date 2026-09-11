# Long explanatory LLVM blocks

Twelve manually selected, intact upstream comment blocks, 102–263 words,
from LLVM 10.0.0 at `d32170dbd5b0d54436537b6b75beaf44324e0c28` (March 2020).
These are new files, disjoint from the initial short-comment corpus. Every
reference is extracted verbatim from hash-locked source; none is a generated
rewrite. Historical provenance is not an individual authorship attestation.

| Split | File | Original start line | Words | Blank-line units |
| --- | --- | ---: | ---: | ---: |
| Train | GVN.cpp | 2631 | 125 | 2 |
| Train | JumpThreading.cpp | 546 | 153 | 2 |
| Train | SROA.cpp | 1564 | 144 | 3 |
| Train | SROA.cpp | 3599 | 243 | 5 |
| Validation | MemoryDependenceAnalysis.cpp | 451 | 241 | 1 |
| Validation | MemoryDependenceAnalysis.cpp | 1080 | 102 | 4 |
| Validation | LazyValueInfo.cpp | 81 | 149 | 1 |
| Validation | LazyValueInfo.cpp | 1873 | 178 | 1 |
| Test | LoopUnswitch.cpp | 124 | 131 | 2 |
| Test | LoopUnswitch.cpp | 1063 | 140 | 1 |
| Test | BasicAliasAnalysis.cpp | 200 | 197 | 5 |
| Test | BasicAliasAnalysis.cpp | 1241 | 263 | 6 |

Eight references contain multiple blank-line-separated units; four are dense
blocks with multiple sentences, lists or examples without blank separators.
Counts include IR/example tokens, so they do not measure prose alone. Selection
requires substantial explanation and excludes license banners. All cases have
at least five heuristic sentences. Neither sentence nor paragraph heuristics
are quality ratings.

`sources.json` and `sources.lock.json` retain the 12-file discovery pool,
including unused files. Selected references use seven files, with file-disjoint
4/4/4 splits. `selection.json` records context windows and length bounds;
`cases.json` adds exact reference hashes. Context bounds were reviewed before
generation to include complete relevant routines and avoid unnecessary nearby
functions. JumpThreading also has two explicit caller excerpts; these cannot
overlap the hidden reference. The loader checks hashes, split assignment,
word bounds and reference leakage before any model call.

This is not random or representative sampling. Selection and context choices
were made before seeing generated results, but the construction agent saw
reference text to select locations. Generators receive only masked excerpts
and the shared task, not the reference, judge rubric, checkout or history.
Missing historical intent and possible pretraining memorization remain
limitations. See the [protocol](../../experiments/long-blocks/PROTOCOL.md).

Verify this stratum without model calls:

```sh
python -m claudish verify-corpus --corpus-dir corpus/long-blocks
```

Keep the initial corpus and old results intact. To create another stratum,
use a new directory with `sources.json` and `selection.json`, then
`prepare-corpus --corpus-dir <directory>`. Do not silently replace a frozen
selection or use exposed test results for tuning while calling them held out.
