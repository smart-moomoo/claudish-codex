# Archived candidates

These files preserve the versions on main at
`7870906316b86af20753367c1d0579884a1225aa`, before the editorial rebuild.
They are historical inputs, not sources for the current build. Do not edit or
regenerate them when the current guidance changes.

| File | Purpose |
| --- | --- |
| `scaled-comments.md` | Standalone ten-rule comment guide used by the scaled study |
| `scaled-base.md` | That guide's base instructions |
| `scaled-entries.json` | That guide's dictionary, including reviewer metadata |
| `changes-v1.md` | General-change guide before the editorial rebuild; not validated by the scaled study |

The SHA-256 of `scaled-comments.md` is
`f271a6340124c2b3b748f0ca1c1d164c8286ebfc66a8da3b4337a6c6934d7bb9`.
Its body hash, excluding the first provenance line, is
`e1c9b98ce9233a16622f910976cc407ca00b22f283e8f8233a6323c00f07997f`;
this matches `experiments/scaled/frozen-candidate.json`.

Use `--spec specs/archive/scaled-comments.md` for a new run with that candidate.
Use the matching frozen corpus, task and rubric from the study protocol too.
To reconstruct the old builder, inspect the commit above; the current builder
also consumes shared prose principles and intentionally produces a new guide.
Saved historical runs retain their own spec and dictionary snapshots.
