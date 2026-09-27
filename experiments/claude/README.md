# Claude counterpart: whole-change study

The revised guide preserved a user consequence that all three initial
conditions deleted: stopping and resuming does not pay again for completed
calls. That training improvement does not establish a general advantage.
Both code-containing training cases still had unresolved review concerns;
the historical preservation controls did not distinguish the guides.

Use [the guide](../../specs/claude-changes.md) through the
[whole-change workflow](../../docs/claude.md). Its prose instructions come from
pinned upstream Claudish, not the Codex guide. A separate extension permits
behavior-preserving code refactoring and whole-document reorganization.

## Inputs and comparisons

Each condition receives complete files, parent versions, the task and context.
No large commit was reduced to selected hunks.

| Input | Split | Files | Added + removed lines |
| --- | --- | ---: | ---: |
| Fresh Opus 5.5 explanation of saved-work code | Train | 1 | 13 |
| Claude-attributed resume commit | Train | 5 | 348 |
| Claude-attributed evaluation commit | Train | 12 | 2,121 |
| Historical Click small commit | Test | 1 | 2 |
| Historical Click medium commit | Test | 2 | 14 |
| Historical Click large commit | Test | 35 | 15,289 |

Line counts describe the diff, not explanation length; the document input is
the complete model answer. Commit coauthor trailers establish attribution,
not the origin of every line. Click 7.1.2 history supplies human-era preservation
controls, not verified Claude outputs or individual human attestations.
Selection, revisions and input hashes are in [frozen.json](frozen.json).

Fresh local `claude-opus-5-5` sessions at medium effort compare a plain cleanup
request, the unmodified upstream guide, and the counterpart. Fresh
`codex exec` judges use `gpt-5.6-sol`, medium effort, with the same fixed
[rubric](../../evaluation/change-rubric-v2.md), anonymous conditions and no
evolving dictionary. Upstream forbids executable changes; the counterpart
allows refactoring. Code differences therefore are not pure prose improvements.

## Results and failures

Round 1 ran all three conditions on all three training inputs. All nine
generations completed; two document reviews failed exact-quote validation.
All three conditions dropped the explicit stop/resume cost consequence.
The counterpart and plain conditions also repaired a visible caller/callee
keyword mismatch in the large training input. Some upstream edits changed
executable code despite its preservation instruction.

Round 2 ran only the revised counterpart on all three training inputs, keeping
the original plain/upstream comparisons and all previous failures. The guide
adds evidence-linked rules to retain the consequence as well as the mechanism
and to name what a check establishes. The new resume output kept the cost
consequence, bounded by unfinished calls; the explanatory document replaced a
blanket guarantee with concrete checks. All three reviews validated, but the
two code-containing cases remained blocked. Review concerns include inherited
contracts, not just rewrite regressions. Both cases changed executable Python
ASTs; no generated code was executed or certified correct.

After freezing the guide, all nine test generations completed. The six
small/medium reviews passed the applicable criteria. All three large-case
reviews hit the CLI character limit; their failures remain in the report.
The three large outputs were identical no-ops. Lossless deduplication of
identical complete strings let one fresh judge review that shared input: all
51 artifacts passed. This is one judgment, not three independent ratings.

The transport repair was informed by a test failure. It changes no guide,
task or rubric, but the recovery is post-hoc and these test cases are retired
as untouched holdouts. See the explicit [amendment](transport-amendment.json).
All three conditions had two no-ops across the test cases, with no executable
Python AST changes. These controls support preservation on these examples,
not superiority of the counterpart or correctness of the resulting code.

The study made 22 Claude calls including discovery, and 22 Codex judge
attempts including the single recovery. Three Codex attempts were rejected at
the CLI input limit before inference. CLI cost estimates are not subscription
bills. [results.json](results.json) retains original per-condition outcomes,
aggregate metrics and call metadata; the recovery is separate. See
[ITERATIONS.md](ITERATIONS.md) for candidate changes and parser recovery.

## Reproduce the procedure

Original prompts, answers, generated patches and downloaded sources remain
local under ignored `runs/`. Published hashes allow an owner of those files
to check them; the public report alone cannot reproduce the exact private
answers. New model calls produce new samples, not replacements for this study.

With authenticated CLIs and this repository's full Git history, prepare a new
study in unused directories. The first command makes a paid model call:

```sh
python3 -m experiments.claude.generate_example --out runs/new-claude-discovery
git clone --branch 7.1.2 --depth 100 https://github.com/pallets/click.git runs/new-click
python3 -m experiments.claude.prepare_study --out runs/new-claude-cases \
  --click-repo runs/new-click --discovery runs/new-claude-discovery
```

Use the [CLI instructions](../../docs/claude.md#compare-the-three-conditions)
to supply all case paths while selecting the training split. Follow the
[protocol](PROTOCOL.md): inspect training contrasts, retain every attempt,
freeze choices before evaluation, and choose new file-disjoint holdouts.
Do not use these now-exposed Click cases to select another candidate and
claim a fresh test. No experiment writes to the source repository or upstream.
