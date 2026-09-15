# Plain-English code comments for Codex

Write comments that belong beside the surrounding code. Explain intent, a
constraint, or behavior a reader needs to know. Preserve facts, conditions,
negation, uncertainty, names, and technical distinctions.

Before drafting, identify the local operation, its condition and consequence,
and any non-obvious reason for the chosen type, order, check, or restart. Read
the actual code around the location, including bounds and special cases.
Include the information a maintainer would otherwise have to reconstruct.
Match the scope of the location. A local operation may need only one sentence;
a function or algorithm comment may need several paragraphs. Explain the
problem and the important mechanism, then the constraints a maintainer needs.
Infer that scope from placement and neighboring conventions. A marker before
one statement or compact block does not request documentation for the entire
function. Default to the shortest comment that preserves the local non-obvious
fact; expand only when the code at that location needs a contract, rationale,
example, or interacting constraints.
Keep return-value contracts, significant fallbacks, and reasons for doing work
in a particular order. Do not turn a long block into a tour of every statement,
temporary variable, cleanup step, or downstream caller.
Check every explanatory claim against the code. A condition that permits an
update does not establish what happens when that condition is false.
Keep approximations, heuristics, and conservative restrictions qualified.
An implementation's refusal to handle a case does not prove that case is
impossible or inherently unsafe. Do not invent reasons to fill out a paragraph.

Use familiar verbs and concrete subjects. Omit rhetorical introductions,
decorative metaphors, invented compound labels, and repeated conclusions.
Do not add an explanation the code and task do not support. Keep precise
compiler terminology when it carries meaning. A short comment is useful only
if it still says what a maintainer needs.

Match the neighboring comment conventions, including Doxygen commands where
appropriate. Comment text is prose, not a conversation with the user.

The patterns below are examples to interpret in context, not banned words or
mechanical replacement rules. Their examples are synthetic illustrations.
