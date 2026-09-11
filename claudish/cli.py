"""Command-line entry point. All LLM calls go through codex exec."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import subprocess

from . import corpus, diff, experiment, spec
from .io import digest, write_json
from .judge import evaluate
from .metrics import measure
from .runner import MODEL, EFFORT


def llm_options(parser):
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--effort", default=EFFORT, choices=("low", "medium", "high", "xhigh", "max"))
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=240, help="Seconds allowed per Codex call")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Claudish project directory")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-spec", help="Generate the spec from the dictionary")
    build.add_argument("--check", action="store_true")
    prepare = commands.add_parser("prepare-corpus", help="Fetch pinned LLVM source and freeze selected references")
    verify = commands.add_parser("verify-corpus", help="Verify source and reference hashes and split isolation")
    for command in (prepare, verify):
        command.add_argument("--corpus-dir", type=Path, help="Corpus directory, relative to --root or absolute")
    ablation = commands.add_parser("ablate", help="Run fresh paired agents on an LLVM corpus split")
    ablation.add_argument("--split", choices=("train", "validation", "test"), default="train")
    ablation.add_argument("--out", required=True, type=Path)
    ablation.add_argument("--spec", type=Path)
    ablation.add_argument("--corpus-dir", type=Path)
    ablation.add_argument("--task", type=Path, help="Shared generation task, relative to --root or absolute")
    ablation.add_argument("--rubric", type=Path, help="Fixed judge rubric, relative to --root or absolute")
    ablation.add_argument("--repeats", type=int, default=1)
    ablation.add_argument("--seed", type=int, default=42)
    llm_options(ablation)
    replay = commands.add_parser("replay", help="Rebuild reports from saved calls without invoking Codex")
    replay.add_argument("--run", type=Path, required=True)
    grade = commands.add_parser("grade-diff", help="Grade added/changed comments in a C/C++ diff")
    grade.add_argument("--diff", required=True, type=Path, help="Unified diff, or - for stdin")
    grade.add_argument("--base-dir", required=True, type=Path, help="Source tree BEFORE applying the diff")
    grade.add_argument("--out", required=True, type=Path)
    grade.add_argument("--extract-only", action="store_true", help="Extract changed comments without calling an LLM")
    llm_options(grade)
    args = parser.parse_args(argv)
    try:
        if args.command == "build-spec":
            result = spec.build(args.root, args.check)
        elif args.command == "prepare-corpus":
            result = corpus.prepare(args.root, args.corpus_dir)
        elif args.command == "verify-corpus":
            result = {"verified_cases": len(corpus.cases(args.root, corpus_dir=args.corpus_dir))}
        elif args.command == "ablate":
            result = experiment.run(args.root, args.out, split=args.split, repeats=args.repeats,
                                    seed=args.seed, spec_path=args.spec, jobs=args.jobs,
                                    corpus_dir=args.corpus_dir, task_path=args.task, rubric_path=args.rubric,
                                    model=args.model, effort=args.effort, timeout=args.timeout)
        elif args.command == "replay":
            result = experiment.replay(args.run)
        else:
            if not 1 <= args.jobs <= 8:
                raise ValueError("Use between 1 and 8 jobs")
            text = sys.stdin.read() if str(args.diff) == "-" else args.diff.read_text()
            extracted = diff.extract(text, args.base_dir)
            args.out.mkdir(parents=True, exist_ok=False)
            write_json(args.out / "extracted.json", extracted)
            if args.extract_only:
                result = extracted
            else:
                rubric = (args.root / "evaluation/rubric.md").read_text()
                (args.out / "rubric.md").write_text(rubric)
                def judge_one(comment):
                    # No reference is inferred for a user-supplied diff.
                    judged = evaluate(comment["context"], {"comment": comment["comment"]}, rubric,
                                      args.out / "calls" / digest(comment["id"])[:16],
                                      model=args.model, effort=args.effort, timeout=args.timeout)
                    return {**comment, "grade": judged["grades"]["comment"], "metrics": measure(comment["comment"])}
                with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                    grades = list(pool.map(judge_one, extracted["comments"]))
                result = {"model": args.model, "effort": args.effort, "rubric_sha256": digest(rubric),
                          "diff_sha256": digest(text), "comments": grades,
                          "authorship": "User-supplied attribution; a diff alone cannot establish Codex authorship.",
                          "old_comments_touched": extracted["old_comments_touched"]}
                write_json(args.out / "grades.json", result)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, RuntimeError, OSError, KeyError, StopIteration, subprocess.SubprocessError) as exc:
        print(f"claudish: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
