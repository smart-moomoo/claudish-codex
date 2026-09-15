# Rebuilding the editing guidance

This revision responds to the user's review of the self-edit feature branch.
It rebuilds the guidance and applies it to main; it does not merge that branch
or relabel its earlier rewrites as successes. The examples below are development
cases supplied in that review, not an independent holdout or human calibration.

## The replacement

The old ten-entry dictionary concentrated on avoiding patterns. The replacement
starts with a positive writing target and six operations: state the action,
keep the consequence, preserve certainty, delete only redundancy, choose the
needed scale, and organize the explanation. `specs/prose-base.md` maintains the
shared principles; both generated guides include them once. There is no banned
phrase list or instruction to minimize the line count.

Before rewriting, identify the statements and implications that must survive.
Choose the document's organization before polishing its sentences. Check that
every removal either loses no meaning or leaves that meaning explicit elsewhere.
Treat factual corrections as a separate, evidenced operation.

The README now introduces the project and its first useful action before the
criteria. Results are grouped by what they establish, rather than study order.
Detailed grading instructions and experiment operations moved to
[reviewing](reviewing.md) and [experiments](experiments.md), with warnings kept
beside the actions they qualify. The tiers module now explains the ladder and
its limits together rather than ending with a detached qualification.

## Preserved meaning and explicit corrections

| Passage | Required result and evidence |
| --- | --- |
| `judge.blind_labels` | Keep the reason for reproducible labels: reading a saved judgment under its original labels. Correct "seed alone": the function shuffles `list(comments)`, so the input arm order also matters. |
| `experiment.resume` | Keep the user consequence: stopping does not make you pay again for saved, completed calls. `_completed` reads the saved answer before generation or judging. Calls without a saved answer may run again. Removing the cost implication was not an improvement; the earlier feature report's interpretation is rejected here. |
| `tiers` module | Keep the ability to apply a different threshold without new model calls. Explain that meaning is reported alongside the ladder, not enforced as a gate. Calling it a "precondition" falsely suggested enforcement. |
| `tiers.code_shaped` | Replace "never ordinary prose" with the actual predicate: underscore, a multi-character uppercase token, or an ASCII lowercase-to-uppercase transition. `NASA` satisfies the uppercase test and can occur in prose; the old universal claim was false, not merely too confident. |
| `tiers.measure_comment` | State which tokens the metrics count. Absence from the file does not establish ownership by another component or prove future breakage; those conclusions went beyond the calculation. |
| `placement` and `placement.anchors` | Keep the selection mechanism and its purpose. Identical markers hide the choice in the marker itself; blank-line and nearby-comment checks select comparable boundaries. The model still sees surrounding source, so neither the marker nor those checks prove that the case kinds are indistinguishable. |

These corrections follow the implementation on main. They are not exceptions
that permit arbitrary hedging: when the evidence establishes a guarantee, the
new guidance requires keeping it just as strongly.

## Review and evidence boundaries

Mixed-change review version 2 reads complete artifacts, checks lost reasons
and certainty changes, and assesses paragraph order and placement. Meaning loss
can block a change regardless of style scores. Cleanliness and effectiveness
still apply only to comments; invasiveness and optimality apply to text,
comments and code. The result schema is unchanged, but the rubric and review
version change together so new reviews cannot be mistaken for version 1.

The old rubric, published LLVM outputs, references and frozen protocols remain
unchanged. The old generated guides and comment sources are
[archived](../specs/archive/README.md). Current guides are new editorial
candidates; the dictionary's empty evidence lists claim no measured improvement.
No fresh model experiment or independent model review is claimed for this
revision. A future comparison needs a fixed rubric, fresh baselines and a new
holdout after development choices are frozen.

Verification targets generation dependencies, provenance and review contracts.
The 18 focused checks in `test_spec.py` and `test_changes.py` passed. Archived
files were compared byte-for-byte with main's originals, local documentation
links resolved, and the four explanation-only modules retained identical ASTs
after removing docstrings. These checks cannot establish prose quality.
Runtime changes are limited to guide
assembly and selecting the version-2 mixed-change rubric; the edited experiment,
judge, placement and tier modules retain their executable logic and prompts.
There was no implementation defect in those modules to fix merely because
their explanations were wrong. This is not a rule against refactoring code.
