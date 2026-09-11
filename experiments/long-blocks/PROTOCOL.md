# Long-block resampling protocol

Recorded before any long-block generation. The original study's 12–38-word
references do not establish how Codex writes substantial comment blocks.

Select 12 new, intact comment blocks of 100–300 words from the same immutable
LLVM 10.0.0 commit. This is a deliberately length-stratified, manually selected
sample, not a random LLVM sample. Four training cases come from GVN,
JumpThreading and SROA; four validation cases from MemoryDependenceAnalysis
and LazyValueInfo; four test cases from LoopUnswitch and BasicAliasAnalysis.
Split by file, with no files from the initial study. Freeze all locations and
context windows before generation. Inspect reference text only for corpus
construction; tune only on training outputs. Historical provenance is evidence
of pre-assistant upstream text, not an individual authorship attestation.

Candidate discovery examined 12 files listed in sources.json. LoopSimplify and
LiveIntervals had no eligible blocks; MachineBlockPlacement is unsupported by
the conservative scanner. Other unselected files/blocks were skipped to favor
explanatory prose over token-heavy diagrams or short API descriptions. Keep
the discovery source lock and downloads, including unselected files. Before
selection was frozen, LoopUnswitch was assigned to test to provide a second
test file. No generated outcomes informed selection or split assignment.

Some selected blocks contain useful IR/examples; word counts include their
tokens and are not pure prose counts. Paragraphs are blank-line-separated
units, including examples and lists, not measures of quality. Record word,
sentence and paragraph counts, repetition, lexical distance and all six fixed
judge deficits. Do not reward verbosity, deletion, word overlap or padding.

Both arms receive evaluation/long-block-task.md and identical expanded code
excerpts; the original reference is removed. Extra excerpts expose relevant
call sites when a tiny function alone cannot show its design constraints.
No checkout or reference text reaches generators. Unknown historical intent
and pretraining memorization remain limitations.

Start with the existing seven-rule spec, unchanged from the initial series.
Use the original evaluation/rubric.md unchanged throughout this series. The
judge does not receive the spec or dictionary. The upstream block is included
under a randomized label and also as factual reference: condition-blind, not
fully reference-blind. Keep its mistakes visible. All fresh calls use
codex exec, gpt-5.6-sol, medium effort, the existing isolated environment,
one repeat and at most two concurrent calls.

Run four training pairs and four judges (12 calls). If failures justify it,
make at most one training-derived spec revision and rerun those four pairs
with fresh calls (12 additional calls). Freeze the selected candidate before
validation and test (24 calls total). No holdout-driven retuning. Expected
budget: 36 calls without a revision, at most 48 with one, excluding explicitly
reported infrastructure failures; never rerun completed calls just to change
the result. Preserve all outputs and regressions.

Use the initial advisory promotion screen: a mean style improvement with no
paired meaning regression and no increase in mean usefulness deficit. A pass
does not establish significance or human preference. Inspect actual comments
as well as judge scores. Do not claim that a floor-scoring LLM judge proves
human-like writing. Do not pool these results with the short-block series:
the reference stratum, shared task, code contexts and descriptive metrics have
changed. No smoke tests, checkpoints, upstream writes or broad test reruns.

The CLI isolation follows the [official non-interactive-mode documentation](https://learn.chatgpt.com/docs/non-interactive-mode).
The requested [gpt-5.6-sol model](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
and medium effort are preserved; no model substitution is made.
