# Claude evidence v2 candidate

Use the complete [generated guide](../artifacts/claude-evidence-v2.md), not just
the [editable base](claude-evidence-v2-base.md). This candidate remains separate
from the maintained Claude artifact. The [PhiValues results](../../experiments/claude/llvm/PHIVALUES-RESULTS.md)
show partial recovery, not a complete fix or evidence of general reliability.

The base contains the full experimental revision, including the earlier
contract-review guidance. The latest change requires each added behavior or
structure to have an explicit requirement or reachable failure and a motivated,
in-scope test case. It rejects speculative inputs and unnecessary tests. Its
explanation-preservation rule is separate from code justification.

## Rebuild the evaluated snapshot

Use a separate checkout of source commit
`33546593d16a10f7394d9764b6eb941c38fe7f2f`, which contains the Claude builder,
dictionary and pinned upstream sources. Replace that checkout's
`specs/claude-base.md` with `claude-evidence-v2-base.md` from this directory.
Leave its dictionary, vendor files and evidence records unchanged. Run:

```sh
python3 -m claudish build-claude-spec
```

The resulting `specs/claude-changes.md` must have SHA-256
`b94858066b9087a4c019145ce3c256dfe56649fc96031144f6d138e841fe0a83`.
The published artifact is a byte-for-byte copy of that generated file; do not
edit it directly. Include the [upstream license](../artifacts/LICENSE.claudish)
when redistributing it.

Only the source, generated guide and evaluation summaries are published here.
Private inputs, prompts, answers, detailed reviews and session files remain local.
