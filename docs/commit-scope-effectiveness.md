# Code effectiveness within the current commit

The user requested adding the same commit-scope effectiveness guidance to the
Codex and Claude specs. Effectiveness now applies to code as well as comments
and docstrings; cleanliness remains specific to comments/docstrings. Other prose
continues to use invasiveness and optimality.

The change defines commit scope through the intended behavior change or
simplification, required input domain and preserved contracts. Necessary caller,
interface, documentation and test updates belong to that scope. A speculative
future caller, an excluded input or uncertainty alone does not justify a new
check, fallback, retry or default. Existing required validation and recovery stay;
changes to callers or representations may invalidate a previous guarantee.

The synthetic example distinguishes an unnecessary null-to-default fallback
under a preserved non-null caller contract from required parser rejection of
malformed external inputs. It is an explanatory example, not an observed trial
or a new human reference. Scope cannot be narrowed to excuse a requested case.

Both maintained sources contain the guidance independently. The Codex guide is
rebuilt with the main-branch builder; the Claude guide uses the pinned builder,
dictionary and vendor inputs described in [claude-source.md](../specs/claude-source.md).
The generated artifacts remain byte-for-byte copies of those builds.

This is a user-requested editorial revision. No new model experiment or measured
performance claim accompanies it. The version-2 reviewer, its schema and existing
evaluation results are unchanged; [change-scope.md](change-scope.md) documents the
difference between current guide scope and the existing reviewer contract.

Both generated-spec freshness checks passed. The existing focused suites passed
8 spec-generation checks, 10 mixed-change review checks, and the Claude builder's
source-independence/pinned-input check. Both published artifacts match their
generated outputs byte for byte; the shared commit-scope addition is identical.
The frozen rubric, reviewer implementation, Codex comment-only guide and upstream
Claude inputs retain their prior contents. These checks establish build and
artifact consistency, not a measured improvement in agent behavior.
