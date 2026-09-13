# Scaled LLVM study

The scaled study is complete. It used 150 comments from previously unexposed,
file-disjoint LLVM 10.0.0 sources: 75 training, 40 validation and 35 test.
Every pair used fresh baseline and treatment sessions, followed by two fresh
anonymous judges. All calls used `codex exec`, `gpt-5.6-sol`, and medium
reasoning. See the preregistered [protocol](PROTOCOL.md), frozen
[candidate](frozen-candidate.json), and machine-readable aggregate
[results](results.json). That file is regenerated from the four run
directories with `python -m claudish aggregate`; it is not maintained by hand.

Scores are deficits from 0 (best) to 4 (worst). Negative paired changes favor
the spec.

| Split | Pairs analyzed | Claudishness | Words | Structure | Simplicity | Meaning | Usefulness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Training, original nine rules | 75 | -0.360 | -0.347 | -0.293 | -0.407 | -0.147 | -0.040 |
| Training, revised ten rules | 75 | -0.400 | -0.347 | -0.280 | -0.353 | -0.247 | -0.060 |
| Validation | 39 of 40 | -0.423 | -0.423 | -0.372 | -0.500 | -0.051 | -0.013 |
| Test | 35 | -0.643 | -0.614 | -0.343 | -0.486 | -0.214 | -0.100 |
| Combined unseen | 74 | -0.527 | -0.514 | -0.358 | -0.493 | -0.128 | -0.054 |

On the combined unseen cases, the 95% bootstrap intervals excluded zero for
all four style dimensions and meaning. Usefulness was directionally better but
inconclusive: -0.054, 95% CI [-0.128, 0.027]. The treatment had seven localized
meaning regressions and no severe meaning regression. It passed the frozen
advisory screen on validation and test.

The main remaining gap is length and factual completeness. Unseen comments
averaged 173 words without the spec, 147 with it, and 77 upstream. The spec
substantially reduced GPT-like style without reproducing the terseness of the
historical comments. Long comments remained the hardest factual stratum.

One validation treatment returned comment delimiters and was excluded without
rerolling. Six of 448 judgments violated the evidence schema and were preserved
but excluded; 442 judgments remained valid. Exact inter-judge agreement on the
combined unseen set ranged from 68.5% for simplicity to 85.4% for usefulness.

The study made 898 model calls and recorded 9,516,038 input tokens, of which
5,657,728 were cached, plus 851,445 output tokens and 536,653 separately
reported reasoning-output tokens. Raw prompts, responses, event streams,
generated diffs, detailed grades, and downloaded LLVM files remain private
local artifacts and are Git-ignored.

These are model-judge measurements on a constructed historical corpus, not a
human preference study or proof of general performance. The generator and
judge share a model family, upstream references can contain stale information,
and pretraining memorization cannot be excluded. Confidence intervals describe
case-level sampling uncertainty within this corpus only.
