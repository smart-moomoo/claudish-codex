"""Command-line entry point. All LLM calls go through codex exec."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import subprocess

from . import changes, commits, corpus, diff, experiment, filelevel, placement, spec, tiers
from .io import digest, read_json, write_json
from .judge import evaluate
from .metrics import measure
from .runner import MODEL, EFFORT


def pair(text):
    """Split a LABEL=VALUE command-line argument."""
    label, separator, value = text.partition("=")
    if not separator or not label.strip() or not value.strip():
        raise ValueError(f"Expected LABEL=VALUE, got: {text}")
    return label.strip(), value.strip()


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
    review = commands.add_parser("review-change", help="Review text, comments and code with scoped criteria")
    review.add_argument("--input", required=True, type=Path, help="Task and typed before/after artifacts as JSON")
    review.add_argument("--out", required=True, type=Path)
    review.add_argument("--model", default=MODEL)
    review.add_argument("--effort", default=EFFORT, choices=("low", "medium", "high", "xhigh", "max"))
    review.add_argument("--timeout", type=int, default=240)
    prepare = commands.add_parser("prepare-corpus", help="Fetch pinned LLVM source and freeze selected references")
    verify = commands.add_parser("verify-corpus", help="Verify source and reference hashes and split isolation")
    for command in (prepare, verify):
        command.add_argument("--corpus-dir", type=Path, help="Corpus directory, relative to --root or absolute")
    select = commands.add_parser("select-corpus", help="Freeze a deterministic scaled corpus selection")
    select.add_argument("--corpus-dir", required=True, type=Path)
    select.add_argument("--train", type=int, default=75)
    select.add_argument("--validation", type=int, default=40)
    select.add_argument("--test", type=int, default=35)
    select.add_argument("--seed", type=int, default=20260911)
    select.add_argument("--max-per-file", type=int, default=6)
    ablation = commands.add_parser("ablate", help="Run fresh paired agents on an LLVM corpus split")
    ablation.add_argument("--split", choices=("train", "validation", "test"), default="train")
    ablation.add_argument("--out", required=True, type=Path)
    ablation.add_argument("--spec", type=Path)
    ablation.add_argument("--corpus-dir", type=Path)
    ablation.add_argument("--task", type=Path, help="Shared generation task, relative to --root or absolute")
    ablation.add_argument("--rubric", type=Path, help="Fixed judge rubric, relative to --root or absolute")
    ablation.add_argument("--repeats", type=int, default=1)
    ablation.add_argument("--judges", type=int, default=1, help="Fresh anonymous judgments per generated pair")
    ablation.add_argument("--seed", type=int, default=42)
    llm_options(ablation)
    reaggregate = commands.add_parser("reaggregate", help="Rebuild a run's summary and report from saved rows")
    reaggregate.add_argument("--run", type=Path, required=True)
    combine = commands.add_parser("aggregate", help="Combine finished runs into one published study result")
    combine.add_argument("--run", action="append", default=[], metavar="LABEL=DIR",
                         help="Labelled run directory; repeat for each run")
    combine.add_argument("--combine", action="append", default=[], metavar="LABEL=A,B",
                         help="Pool the rows of named runs under a new label")
    combine.add_argument("--out", type=Path, help="Write the result here instead of stdout only")
    resume = commands.add_parser("resume-run", help="Continue an interrupted or failed run, reusing completed calls")
    resume.add_argument("--run", type=Path, required=True)
    resume.add_argument("--jobs", type=int, default=2)
    resume.add_argument("--timeout", type=int, default=240)
    score = commands.add_parser("score-tiers", help="Score finished runs against the four criteria")
    score.add_argument("--run", action="append", required=True, metavar="DIR or LABEL=DIR",
                       help="Run directory; repeat to pool several runs into one ladder")
    score.add_argument("--out", type=Path, help="Write the pooled result here as well")
    lengths = commands.add_parser("measure-generations",
                                  help="Length and coupling for a run's saved comments, without judges")
    lengths.add_argument("--run", type=Path, required=True)
    place = commands.add_parser("select-placement", help="Freeze positions where a comment may or may not belong")
    place.add_argument("--corpus-dir", required=True, type=Path)
    place.add_argument("--per-split", type=int, default=60)
    place.add_argument("--seed", type=int, default=20260913)
    place.add_argument("--max-per-file", type=int, default=3)
    place.add_argument("--split", action="append", default=[], choices=("train", "validation", "test"))
    decide = commands.add_parser("placement-run", help="Ask fresh agents whether a comment belongs at each position")
    decide.add_argument("--split", choices=("train", "validation", "test"), default="train")
    decide.add_argument("--out", required=True, type=Path)
    decide.add_argument("--spec", type=Path)
    decide.add_argument("--corpus-dir", type=Path)
    decide.add_argument("--task", type=Path)
    decide.add_argument("--cases", type=int, help="Answer only this many positions, kept balanced")
    decide.add_argument("--resume", action="store_true", help="Reuse completed calls in an existing directory")
    llm_options(decide)
    rescore = commands.add_parser("rescore-commits", help="Rescore saved commit answers without model calls")
    rescore.add_argument("--run", type=Path, required=True)
    rescore.add_argument("--out", type=Path, required=True)
    files = commands.add_parser("judge-files", help="Judge each file's comments as a set")
    files.add_argument("--run", type=Path, required=True)
    files.add_argument("--rubric", type=Path, help="Defaults to evaluation/file-rubric.md")
    files.add_argument("--seed", type=int, default=42)
    files.add_argument("--min-comments", type=int, default=filelevel.MIN_COMMENTS)
    files.add_argument("--resume", action="store_true", help="Reuse completed file calls")
    llm_options(files)
    pick = commands.add_parser("select-commits", help="Freeze a corpus of small single-purpose LLVM commits")
    pick.add_argument("--corpus-dir", required=True, type=Path)
    pick.add_argument("--count", type=int, default=40)
    pick.add_argument("--scan", type=int, default=400)
    pick.add_argument("--seed", type=int, default=20260913)
    refetch = commands.add_parser("prepare-commits", help="Refetch the frozen commit sources and patches")
    refetch.add_argument("--corpus-dir", required=True, type=Path)
    check = commands.add_parser("verify-commits", help="Verify frozen commit sources and patches offline")
    check.add_argument("--corpus-dir", required=True, type=Path)
    patch = commands.add_parser("commit-run", help="Ask fresh agents to make a real LLVM change")
    patch.add_argument("--split", choices=("train", "validation", "test"), default="train")
    patch.add_argument("--out", required=True, type=Path)
    patch.add_argument("--corpus-dir", required=True, type=Path)
    patch.add_argument("--spec", type=Path, help="Optional guidance; supplying it turns the run into an ablation")
    patch.add_argument("--task", type=Path)
    patch.add_argument("--overlap-threshold", type=float, default=0.5)
    patch.add_argument("--resume", action="store_true", help="Reuse completed calls in an existing directory")
    llm_options(patch)
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
        elif args.command == "review-change":
            result = changes.review(args.root, args.input, args.out,
                                    model=args.model, effort=args.effort, timeout=args.timeout)
        elif args.command == "prepare-corpus":
            result = corpus.prepare(args.root, args.corpus_dir)
        elif args.command == "verify-corpus":
            result = {"verified_cases": len(corpus.cases(args.root, corpus_dir=args.corpus_dir))}
        elif args.command == "select-corpus":
            result = corpus.select_stratified(
                args.root, args.corpus_dir,
                {"train": args.train, "validation": args.validation, "test": args.test},
                seed=args.seed, max_per_file=args.max_per_file)
        elif args.command == "ablate":
            result = experiment.run(args.root, args.out, split=args.split, repeats=args.repeats,
                                    judges=args.judges,
                                    seed=args.seed, spec_path=args.spec, jobs=args.jobs,
                                    corpus_dir=args.corpus_dir, task_path=args.task, rubric_path=args.rubric,
                                    model=args.model, effort=args.effort, timeout=args.timeout)
        elif args.command == "reaggregate":
            result = experiment.reaggregate(args.run)
        elif args.command == "aggregate":
            result = experiment.aggregate(
                [pair(item) for item in args.run],
                [(label, members.split(",")) for label, members in map(pair, args.combine)])
            if args.out:
                write_json(args.out, result)
        elif args.command == "resume-run":
            result = experiment.resume(args.run, jobs=args.jobs, timeout=args.timeout)
        elif args.command == "score-tiers":
            labelled = [pair(item) if "=" in item else (Path(item).name, item)
                        for item in args.run]
            result = {label: tiers.score_run(path, experiment.reload_corpus)
                      for label, path in labelled}
            if len(labelled) > 1:
                result = {"runs": result, "pooled": tiers.combine(labelled)}
            if args.out:
                write_json(args.out, result)
        elif args.command == "measure-generations":
            result = tiers.measure_generations(args.run, experiment.reload_corpus)
        elif args.command == "select-placement":
            result = placement.select(args.root, args.corpus_dir, per_split=args.per_split,
                                      seed=args.seed, max_per_file=args.max_per_file,
                                      splits=tuple(args.split) or ("train",))
        elif args.command == "placement-run":
            result = placement.run(args.root, args.out, split=args.split, jobs=args.jobs,
                                   spec_path=args.spec, corpus_dir=args.corpus_dir,
                                   task_path=args.task, model=args.model, effort=args.effort,
                                   timeout=args.timeout, resume=args.resume, limit=args.cases)
        elif args.command == "rescore-commits":
            result = commits.rescore(args.run, args.out)
        elif args.command == "judge-files":
            manifest = read_json(args.run / "manifest.json")
            rubric = (args.root / (args.rubric or "evaluation/file-rubric.md")).read_text()
            result = filelevel.judge_run(args.run, experiment.reload_corpus(manifest), rubric,
                                         seed=args.seed, jobs=args.jobs, reuse=args.resume,
                                         min_comments=args.min_comments, model=args.model,
                                         effort=args.effort, timeout=args.timeout)
        elif args.command == "select-commits":
            result = commits.select(args.root, args.corpus_dir, count=args.count,
                                    scan=args.scan, seed=args.seed)
        elif args.command == "prepare-commits":
            result = commits.prepare(args.root, args.corpus_dir)
        elif args.command == "verify-commits":
            result = {"verified_commits": len(commits.cases(args.root, corpus_dir=args.corpus_dir))}
        elif args.command == "commit-run":
            result = commits.run(args.root, args.out, split=args.split, jobs=args.jobs,
                                 spec_path=args.spec, corpus_dir=args.corpus_dir,
                                 task_path=args.task, model=args.model, effort=args.effort,
                                 timeout=args.timeout, resume=args.resume,
                                 overlap_threshold=args.overlap_threshold)
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
