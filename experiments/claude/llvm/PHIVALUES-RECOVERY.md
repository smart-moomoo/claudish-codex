# Network recovery for the focused revision

The first context-only call ran in a network-restricted sandbox. Its retained
events contain initialization and eight API retries with no HTTP status, no
assistant answer and no final usage result. The stalled Claude child was stopped
with SIGTERM; the driver saved the failure and scheduled no rewrites or reviews.
No inference or zero usage can be conclusively claimed from those events.

Allow one infrastructure retry with approved network access. Keep the candidate,
seed, guides, rubric and inference settings unchanged. Retain the first attempt
under `runs/claude-llvm/manual-challenge/phivalues-revision-2/`; use the separate
`phivalues-revision-2-network/` directory for the comparison. Use the same driver
with only its BASE path changed at invocation. This adds at most one context
attempt to the original budget, not another rewrite or another sampled output.
If the recovery fails, stop rather than retry again.
