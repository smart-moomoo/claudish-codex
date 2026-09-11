# Initial LLVM iteration protocol

Recorded before the first generation run.

Use Codex CLI `codex exec`, `gpt-5.6-sol`, medium reasoning for both generation
and judging. Each call starts a new ephemeral session in a temporary directory
and Codex home containing only authentication. Personal guidance, memories,
skills and past outputs are excluded. Generation arms differ only in the
project AGENTS.md spec. Tools and web search are disabled. Unexpected tool
execution invalidates a call. Never resume a generator or judge conversation.

The source is LLVM 10.0.0, pinned to commit
`d32170dbd5b0d54436537b6b75beaf44324e0c28`. Use six training cases from StringRef.cpp
and Local.cpp, four validation cases from LoopInfo.cpp, and four test cases
from BasicBlockUtils.cpp. Selection is frozen before generation. These are
manually chosen comment locations spanning intent, constraints, semantics and
algorithms, not a random or representative sample of LLVM. No AI-generated
text is a human reference. Original comments are extracted verbatim, with
source hashes and line links. Historical provenance predates modern code
assistants but cannot independently attest individual authorship.

Task: reconstruct one masked comment from a bounded source excerpt. The
generator does not receive the reference comment, original checkout, commit
history, or judge rubric. Both arms get identical source context. Some
historical rationale may be impossible to reconstruct from code alone;
record missing information instead of claiming a style prompt fixed it.
Pretraining memorization remains possible and cannot be eliminated by masking.

Randomly interleave arms. Grade the two outputs plus the upstream comment
under anonymous, randomized labels using a fixed rubric. The judge sees the
upstream comment as a factual reference. Thus style labels are concealed, but
the judge can recognize the reference's wording: this is not fully blinded
reference evaluation. The judge never sees the spec or dictionary. Measure
word counts, word length, sentence structure, compounds, repetition and
lexical distance independently. Distances describe resemblance, not quality.

Run the initial spec on training cases, inspect failures, revise dictionary
rules and/or base instructions, and run another fresh paired training round.
Use at most three training revisions in this initial study. Keep every round,
including regressions. Freeze a candidate before validation. Freeze the final
choice before test evaluation and do not retune on test results. If tuning
continues later, the exposed test set becomes development data and a new
holdout is required.

Promotion screen: improve at least one mean style dimension with no paired
meaning regressions and no increase in mean usefulness deficit. This is an
advisory screen, not an automatic claim of success. Review individual examples;
the LLM judge can be wrong. Do not optimize word overlap or brevity alone.
The initial sample is descriptive and single-repeat. It does not establish
statistical significance, judge-human agreement, or broad LLVM generalization.
Future evidence requires more files, repeated draws, a second judge and human
ratings collected from actual reviewers. Never synthesize those ratings.
