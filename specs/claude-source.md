# Claude guide source

Use the complete [generated guide](artifacts/claude.md), not just
the [editable base](claude-base.md). This is the sole published Claude artifact,
as requested by the user. The [PhiValues results](../experiments/claude/llvm/PHIVALUES-RESULTS.md)
show partial recovery, not a complete fix or evidence of general reliability.

The base preserves the earlier contract-review guidance and now explicitly
applies effectiveness to code within the scope of the current commit. Checks and
fallbacks must serve an in-scope requirement or reachable failure; required
validation and recovery remain. The existing added-code and test-case rules
remain alongside this extension. [Change record](../docs/commit-scope-effectiveness.md).
This user-requested editorial revision has no new model evaluation.

## Rebuild the published snapshot

Use a separate checkout of source commit
`33546593d16a10f7394d9764b6eb941c38fe7f2f`, which contains the Claude builder,
dictionary and pinned upstream sources. Replace that checkout's
`specs/claude-base.md` with `claude-base.md` from this directory.
Leave its dictionary, vendor files and evidence records unchanged. Run:

```sh
python3 -m claudish build-claude-spec
```

The resulting `specs/claude-changes.md` must have SHA-256
`f26ce3e25c7bf77644fd7e0d68c02502c2daaeab14507e3eb3da105e014dffaf`.
The published artifact is a byte-for-byte copy of that generated file; do not
edit it directly. Include the [upstream license](artifacts/LICENSE.claudish)
when redistributing it.

Only the source, generated guide and evaluation summaries are published here.
Private inputs, prompts, answers, detailed reviews and session files remain local.

## Earlier evaluated artifact

The previous published Claude artifact had SHA-256
`b94858066b9087a4c019145ce3c256dfe56649fc96031144f6d138e841fe0a83`
and remains available at commit `67e65a1a167bdd58c3c037205c43af9a13c40486`.
Its focused results do not establish improvement from the current commit-scope
addition. The builder, dictionary and upstream pin are unchanged.
