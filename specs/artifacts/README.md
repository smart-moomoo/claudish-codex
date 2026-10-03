# Standalone generated guides

- [Codex](codex.md): revise text, comments and code with the Codex guide.
- [Claude](claude.md): revise text, comments and code with the upstream-derived
  Claude guide.

Copy the guide for your model into your project and ask the model to follow it.
Neither file needs this package or its dictionary at runtime. Include
[LICENSE.claudish](LICENSE.claudish) when redistributing the Claude guide; it
contains material from upstream Claudish under the MIT license. This project's
own [MIT license](../../LICENSE) also applies to its original material.

These are byte-for-byte generated snapshots, not additional editable sources.
The Codex snapshot comes from commit
`33546593d16a10f7394d9764b6eb941c38fe7f2f`. The Claude snapshot uses the
[current base](../claude-base.md); its evaluated source was first published in
commit `56c5488`.

| Artifact | Generated source | SHA-256 |
| --- | --- | --- |
| `codex.md` | `specs/codex-changes.md` | `27b939526ca0a392ef151fa10240e1f2a089e89f423a785e9c1ffd2efcea28e6` |
| `claude.md` | `specs/claude-base.md` through the Claude builder | `b94858066b9087a4c019145ce3c256dfe56649fc96031144f6d138e841fe0a83` |

To publish an update, rebuild the source guide, replace its snapshot unchanged,
and record the new source commit and hash here. `build-spec` rebuilds the Codex
sources on main; the Claude builder and experiment tooling remain on
[`feature/claude-counterpart`](https://github.com/smart-moomoo/claudish-codex/tree/feature/claude-counterpart).
The snapshots do not update automatically when a source changes.

Both guides are experimental. See the
[Claude study at this revision](https://github.com/smart-moomoo/claudish-codex/blob/33546593d16a10f7394d9764b6eb941c38fe7f2f/experiments/claude/README.md)
and the [main project documentation](../../README.md) for evidence and limits.

## Claude revision: evidence for added code

The [Claude guide](claude.md) requires concrete requirements and in-scope test
cases for added code, rather than preserving defensive structure because its
necessity is uncertain. It rejects speculative inputs and redundant tests.

The focused PhiValues comparison recovered one simplification but left repeated
operand lookups. Its explanation also claimed test coverage without supplied
evidence. See the [results](../../experiments/claude/llvm/PHIVALUES-RESULTS.md).
The user requested this revision as the sole published Claude artifact. It
remains experimental and has not passed the broader promotion gate; replacing
the artifact does not establish additional evaluation success.

The [rebuild instructions](../claude-source.md) reproduce the evaluated snapshot.
The same project and upstream licenses apply.
