# Claude development record

## Discovery

A fresh `claude-opus-5-5`, medium-effort session explained the publicly available
`claudish/saved.py` implementation with source docstrings removed. Its complete
answer is local. The CLI used the requested model and returned structured output,
but the first parser rejected the built-in `agents-md` plugin as if it were a
user customization. The corrected parser permits that exact built-in identity
and checks for absent ancestor instructions, while still rejecting user plugins.
The original failed call was retained and its existing answer recovered offline;
it was not regenerated. This is a real development sample, not a smoke test.

## Round 1

Three training inputs cover a complete explanatory document, a five-file
348-line Claude-attributed resume commit, and a twelve-file 2,121-line
Claude-attributed evaluation commit. Each received plain, pinned-upstream and
counterpart guidance. The fixed judge rubric is `change-rubric-v2.md`.

All three conditions removed the resume input's explicit consequence that
stopping does not forfeit work already paid for. Their rewrite summaries treated
that consequence as a repetition of the caching mechanism. The first counterpart
already said to keep consequences, but that general instruction did not prevent
this failure. Its summary also called the code sound, while an independent review
identified an unverified corpus-integrity guarantee. That review is evidence of
a concern, not proof that the program is incorrect.

The counterpart made executable changes on the large input, including repairing
a `resume` versus `reuse` keyword mismatch visible between a caller and callee.
The plain condition also repaired that mismatch. The upstream condition made
some executable cleanup despite the upstream guide's code-preservation rule;
instruction compliance must therefore be inspected, not assumed from the arm's
name. No generated code was executed or declared correct.

The second candidate adds two contextual dictionary rules. One distinguishes
mechanism from reader consequence and asks where a removed consequence remains
explicit. The other limits verification language to the property actually
checked. Examples are synthetic; the observed model outputs remain local.
The first candidate is retained in `candidates/round-1.md`.

The judge rejected some explanatory-document reviews because evidence quotes
did not match their source exactly. These answers remain excluded, with the
raw responses preserved. The quote validator and rubric were not loosened to
increase the number of passing reviews.

## Round 2 and freeze

The revised counterpart ran on every training input once, retaining round 1's
plain/upstream outputs as unchanged comparison baselines. This avoids paying
to regenerate identical conditions. It is not a selective reroll of failures:
all three inputs receive the new candidate, and every old result remains.
No third candidate was selected using the held-out evidence.

The revised resume output kept the practical cost consequence in both the
README and docstring, and qualified it for unfinished calls. The document
rewrite also replaced a blanket provenance guarantee with the checks actually
performed. Both code-containing inputs had executable Python AST changes.
The independent reviews still found unresolved concerns, including inherited
contracts not established by the implementation. None of these judgments
certifies behavior, and the revision is not a general success claim.

## Large-review transport recovery

All nine held-out generations completed. Six small/medium reviews completed;
the three large reviews failed at the Codex CLI's 1,048,576-character input
limit. The large input was a complete 35-file historical Click change with
15,289 added plus removed lines. No files or hunks were dropped.

The saved large outputs and review inputs were identical across conditions.
A new transport stores identical complete strings once and references them
from the before/after fields. Expanding it must reproduce the exact original
input. This reduced the serialized case from 1,082,300 to 696,441 characters
before the fixed rubric and transport explanation. One fresh review of that
unique input is shared explicitly, not counted as three independent ratings.

The original failures, frozen guide and rubric remain unchanged. The engine
change is recorded in `transport-amendment.json`; this recovery is post-hoc,
not an untouched held-out result. The exposed test cases are retired as fresh
holdouts. The guide was not tuned on their outputs.

The recovery completed with all 51 artifacts receiving `criteria_passed` and
no blockers. All conditions returned the same no-op, so this is preservation
evidence, not evidence that one guide improves this input more than another.
No code was executed, and the shared review does not certify correctness.
