# Attribution

This project builds on the plain-English translation ideas in
[programasweights/claudish](https://github.com/programasweights/claudish),
especially its [Claudish-to-English spec](https://github.com/programasweights/claudish/blob/main/specs/claudish-to-english.md).
The original is an independent parody project. This counterpart is also
unaffiliated with OpenAI, Anthropic, and the LLVM Foundation.

The Claude counterpart vendors the upstream spec and dictionary at revision
`700588cc0c091a96492eb060255780baca96e7c9`. These files and derived guidance
retain the upstream MIT terms in `vendor/claudish/LICENSE`. See
`vendor/claudish/source.json` for source hashes. Local historical Click study
inputs retain Click's BSD license; its downloaded repository includes LICENSE.rst.
They are not relicensed or included in this repository.

`prepare-corpus` downloads verbatim LLVM source from the revision recorded in
the published lock manifests. These local `corpus/**/upstream/` trees and their
preserved `LICENSE.TXT` files are ignored by Git; individual file headers remain
intact. Source excerpts, upstream reference comments and patches produced in
private local `experiments/` run directories inherit the applicable LLVM terms.
They are not relicensed under this project's MIT license. Original code and
published metadata in this project are MIT licensed.

All dictionary before/after pairs are synthetic illustrations. Only the
verbatim historical LLVM references are labelled upstream human reference
material. Codex output and LLM grades are explicitly identified in reports.
