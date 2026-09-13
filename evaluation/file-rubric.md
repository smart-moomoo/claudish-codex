You are reviewing all the comments one C/C++ source file received, together
rather than one at a time. Each set holds every comment written for the same
set of locations in the same file, by one author. Sets reveal neither
authorship nor experiment condition. Do not use tools.

Judge each set as a whole. A set can be made of individually reasonable
comments and still be a poor set: the same point made three times, two
comments that contradict each other, or a long explanation on the obvious
while the subtle location gets a line. Those are what this rubric is for.
Do not re-judge the wording of individual comments; another rubric covers that.

Return the requested JSON. All scores are integer deficits from 0 to 4:
0 = no material problem; 1 = minor; 2 = noticeable; 3 = substantial; 4 = severe.

- redundancy: the same fact, rule or rationale repeated across locations where
  one statement of it would serve. Repeating a term or a type name is not
  redundancy. Restating a genuinely separate instance of a rule is not either.
- consistency: comments in the set that disagree with each other, name the same
  thing differently, or describe the same mechanism in incompatible ways.
  Different levels of detail are not inconsistency by themselves.
- proportion: how the explanation is distributed across the locations. A
  deficit here means effort went where it was not needed and not where it was,
  judged against what the code at each location actually requires. Uniform
  length is not itself a defect, and neither is variation.

Each location is given with the code that follows it, so you can see what each
comment sits on. Quote exact substrings from the set in evidence; do not use
quotation marks around the substrings. Keep evidence empty when there is no
defect. Explain each score briefly. Never infer authorship from style.
