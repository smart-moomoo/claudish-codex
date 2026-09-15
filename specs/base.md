# Plain-English code comments for Codex

Explain what a maintainer needs to understand at this location: the operation,
its conditions, its consequences, and the reason for a non-obvious choice.
Read the code and surrounding comments before drafting. Preserve return-value
contracts, significant fallbacks, mutation order and boundary cases.

Match the explanation to the location. A comment before one statement may
need a sentence; a function contract, algorithm or proof may need paragraphs
and examples. Infer that scope from the code and neighboring conventions,
not from a target length. Keep the explanation's useful reasons as well as its
facts. An unsupported historical or performance rationale is not a substitute
for a reason established by the supplied context.

Use the shared prose principles for both drafting and revision.
Follow neighboring comment syntax and Doxygen conventions. The dictionary
examples are synthetic illustrations, not forbidden words or automatic edits.
