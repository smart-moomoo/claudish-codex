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
Both snapshots use the maintained sources from commit
`11f91bc5fc7bccc0669e20b4a59217e08f624181`. The Codex snapshot is generated from
`specs/changes-base.md` and its existing prose/comment inputs. The Claude
snapshot uses [the current base](../claude-base.md) with the pinned builder and
inputs described in [claude-source.md](../claude-source.md).

| Artifact | Generated source | SHA-256 |
| --- | --- | --- |
| `codex.md` | `specs/codex-changes.md` | `9f2fa1a74fcecc6cab1d7dfac9ba85e03c316618c919770b1586d8d056f74195` |
| `claude.md` | `specs/claude-base.md` through the Claude builder | `f26ce3e25c7bf77644fd7e0d68c02502c2daaeab14507e3eb3da105e014dffaf` |

To publish an update, rebuild the source guide, replace its snapshot unchanged,
and record the new source commit and hash here. `build-spec` rebuilds the Codex
sources on main; the Claude builder and experiment tooling remain on
[`feature/claude-counterpart`](https://github.com/smart-moomoo/claudish-codex/tree/feature/claude-counterpart).
The snapshots do not update automatically when a source changes.

Both guides are experimental. See the
[Claude study at this revision](https://github.com/smart-moomoo/claudish-codex/blob/33546593d16a10f7394d9764b6eb941c38fe7f2f/experiments/claude/README.md)
and the [main project documentation](../../README.md) for evidence and limits.

## Current revision: effectiveness within the commit

Both guides now apply effectiveness to code and explicitly require checks and
fallbacks to serve the current commit's purpose and required input domain.
They retain required validation and recovery, include necessary dependent edits,
and reject speculative defenses and unrelated fallback behavior. The
[change record](../../docs/commit-scope-effectiveness.md) explains the extension.
No new model evaluation is claimed; the existing reviewer retains its versioned
scope. The snapshots are rebuilt from source, including their provenance stamps.

## Earlier Claude revision: evidence for added code

The [Claude guide](claude.md) requires concrete requirements and in-scope test
cases for added code, rather than preserving defensive structure because its
necessity is uncertain. It rejects speculative inputs and redundant tests.

The focused PhiValues comparison recovered one simplification but left repeated
operand lookups. Its explanation also claimed test coverage without supplied
evidence. See the [results](../../experiments/claude/llvm/PHIVALUES-RESULTS.md).
The user requested this revision as the sole published Claude artifact. It
remains experimental and has not passed the broader promotion gate; replacing
the artifact does not establish additional evaluation success.

The [rebuild instructions](../claude-source.md) reproduce the current published
snapshot and identify the earlier evaluated artifact separately.
The same project and upstream licenses apply.
