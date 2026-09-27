# Standalone generated guides

- [Codex](codex.md): revise text, comments and code with the Codex guide.
- [Claude](claude.md): revise text, comments and code with the upstream-derived
  Claude guide.

Copy the guide for your model into your project and ask the model to follow it.
Neither file needs this package or its dictionary at runtime. Include
[LICENSE.claudish](LICENSE.claudish) when redistributing the Claude guide; it
contains material from upstream Claudish under the MIT license. This project's
own [MIT license](../../LICENSE) also applies to its original material.

These are byte-for-byte release snapshots, not additional editable sources.
Both come from commit `33546593d16a10f7394d9764b6eb941c38fe7f2f`:

| Artifact | Generated source | SHA-256 |
| --- | --- | --- |
| `codex.md` | `specs/codex-changes.md` | `27b939526ca0a392ef151fa10240e1f2a089e89f423a785e9c1ffd2efcea28e6` |
| `claude.md` | `specs/claude-changes.md` | `3d0cf6cfa1ee58a1c432d642d040ce6ee443e1db9b4970f38c97fe169a8a0a72` |

To publish an update, rebuild the source guide, replace its snapshot unchanged,
and record the new source commit and hash here. `build-spec` rebuilds the Codex
sources on main; the Claude builder and experiment tooling remain on
[`feature/claude-counterpart`](https://github.com/smart-moomoo/claudish-codex/tree/feature/claude-counterpart).
The snapshots do not update automatically when a source changes.

Both guides are experimental. See the
[Claude study at this revision](https://github.com/smart-moomoo/claudish-codex/blob/33546593d16a10f7394d9764b6eb941c38fe7f2f/experiments/claude/README.md)
and the [main project documentation](../../README.md) for evidence and limits.
