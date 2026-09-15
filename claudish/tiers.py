"""Measure how far comments pass the clean, effective, invasive, optimal ladder.

The ladder counts a criterion only among cases that passed the preceding ones.
Meaning scores appear alongside it, not as a gate: passing the ladder does not
establish that a comment is true.

Judge deficits below 2 pass; the rubric calls 2 "noticeable". Other thresholds
compare the candidate with the upstream comment at the same location. Each
verdict includes the raw measurements, so a reader can apply a different
threshold later without making another model call.
"""

import re
from statistics import mean

from pathlib import Path

from .corpus import LENGTH_BANDS
from .cpp import scan
from .io import digest, read_json, write_json
from .metrics import words

CRITERIA = ("clean", "effective", "invasive", "optimal")
STYLE_DIMENSIONS = ("claudishness", "words", "structure", "simplicity")
ARMS = ("without_spec", "with_spec")
# The rubric calls 2 "noticeable"; lower deficits pass this screen.
NOTICEABLE = 2

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def code_shaped(token):
    """Match an underscore, a multi-character uppercase token, or a-z then A-Z.

    This heuristic also matches prose acronyms such as "NASA". It excludes
    plain words such as "loop" and "size", even when they are identifiers,
    because a comment may need the ordinary word.
    """
    if "_" in token:
        return True
    if len(token) > 1 and token.isupper():
        return True
    return bool(re.search(r"[a-z][A-Z]", token))


def identifiers(text):
    return {token for token in _IDENTIFIER.findall(text) if code_shaped(token)}


def code_only(text):
    """The text with its comments removed, so prose is compared against code.

    Without this an upstream comment is measured against a file that contains
    it, and every name it uses looks local by definition.
    """
    try:
        comments, _ = scan(text)
    except ValueError:
        return text
    kept, last = [], 0
    for comment in comments:
        kept.append(text[last:comment.start])
        last = comment.end
    kept.append(text[last:])
    return "".join(kept)


def length_band(word_count):
    """The corpus band a comment falls in, or below/above its whole range."""
    for name, (low, high) in LENGTH_BANDS.items():
        if low <= word_count <= high:
            return name
    lowest = min(low for low, _ in LENGTH_BANDS.values())
    return "below" if word_count < lowest else "above"


def measure_comment(comment, case):
    """Length and coupling measures for one comment at one location.

    restatement_fraction counts code-shaped tokens also found in the visible
    code, divided by all identifier-like tokens in the comment. Foreign symbols
    are code-shaped tokens absent from the file's code. They can suggest a
    dependency outside the file, but neither measure establishes ownership or
    whether the explanation will become stale.
    """
    tokens = _IDENTIFIER.findall(comment)
    code_tokens = [token for token in tokens if code_shaped(token)]
    visible = identifiers(code_only(case["context"]))
    local = identifiers(code_only(case["source"]))
    restated = [token for token in code_tokens if token in visible]
    foreign = [token for token in code_tokens if token not in local]
    word_count = len(words(comment))
    return {
        "word_count": word_count,
        "length_band": length_band(word_count),
        "code_identifiers": len(code_tokens),
        "restated_identifiers": len(restated),
        "restatement_fraction": len(restated) / max(1, len(tokens)),
        "foreign_symbols": len(foreign),
        "foreign_symbols_per_100_words": 100 * len(foreign) / max(1, word_count),
        "foreign_symbol_names": sorted(set(foreign)),
    }


def _graded(row, arm, keys):
    return {key: mean(item["grades"][arm][key] for item in row["judgments"]) for key in keys}


def case_criteria(row, case, arm, file_judgment=None):
    """Every criterion for one generated comment, each with its own verdict.

    Verdicts are independent. Whether a criterion counts is decided later, by
    the ladder, which stops at the first one a case fails.
    """
    candidate = measure_comment(row["comments"][arm], case)
    reference = measure_comment(case["reference"], case)
    style = _graded(row, arm, STYLE_DIMENSIONS)
    upstream_style = _graded(row, "upstream", STYLE_DIMENSIONS)
    usefulness = _graded(row, arm, ("usefulness",))["usefulness"]
    band_matches = candidate["length_band"] == reference["length_band"]
    result = {
        "precondition": {
            "meaning": _graded(row, arm, ("meaning",))["meaning"],
            "passed": _graded(row, arm, ("meaning",))["meaning"] < NOTICEABLE,
        },
        "clean": {
            "passed": all(style[key] < NOTICEABLE for key in STYLE_DIMENSIONS),
            "deficits": style, "upstream_deficits": upstream_style,
            "beats_upstream": all(style[key] <= upstream_style[key] for key in STYLE_DIMENSIONS),
        },
        "effective": {
            # Two ways to be wrong here: explain the wrong thing, or explain it
            # at the wrong length. Placement is the third and needs its own corpus.
            "passed": band_matches and usefulness < NOTICEABLE,
            "length_band_matches": band_matches, "usefulness": usefulness,
            "length_band": candidate["length_band"],
            "upstream_length_band": reference["length_band"],
            "word_count": candidate["word_count"],
            "upstream_word_count": reference["word_count"],
        },
        "invasive": {
            "passed": (candidate["restatement_fraction"] <= reference["restatement_fraction"] and
                       candidate["foreign_symbols_per_100_words"] <= reference["foreign_symbols_per_100_words"]),
            "restatement_fraction": candidate["restatement_fraction"],
            "upstream_restatement_fraction": reference["restatement_fraction"],
            "foreign_symbols_per_100_words": candidate["foreign_symbols_per_100_words"],
            "upstream_foreign_symbols_per_100_words": reference["foreign_symbols_per_100_words"],
            "foreign_symbol_names": candidate["foreign_symbol_names"],
        },
    }
    if file_judgment is not None:
        result["optimal"] = file_judgment
    return result


def _first_failure(criteria):
    for name in CRITERIA:
        if name in criteria and not criteria[name]["passed"]:
            return name
    return None


def ladder(scored):
    """Pass rates down the ladder, plus a check that the order is real.

    Each rate counts only the cases still standing, so it answers "of the
    comments that got this far, how many cleared the next bar". The ordering
    claim is testable: a case that clears a harder criterion while failing an
    easier one contradicts it, and those cases are listed.
    """
    present = [name for name in CRITERIA if any(name in item for item in scored)]
    summary = {"cases": len(scored), "criteria": present, "reached": {}, "standing": {}}
    standing = list(scored)
    for name in present:
        judged = [item for item in standing if name in item]
        passed = [item for item in judged if item[name]["passed"]]
        summary["reached"][name] = {
            "judged": len(judged), "passed": len(passed),
            "pass_rate_of_standing": len(passed) / len(judged) if judged else None,
            "pass_rate_of_all": len(passed) / len(scored) if scored else None,
        }
        standing = passed
        summary["standing"][name] = len(passed)
    summary["first_failure"] = {
        name: sum(_first_failure(item) == name for item in scored) for name in present}
    summary["first_failure"]["none"] = sum(_first_failure(item) is None for item in scored)
    summary["order_violations"] = []
    for index, name in enumerate(present[1:], start=1):
        easier = present[index - 1]
        offenders = [item["id"] for item in scored
                     if name in item and easier in item
                     and item[name]["passed"] and not item[easier]["passed"]]
        summary["order_violations"].append(
            {"harder": name, "easier": easier, "cases": len(offenders), "ids": sorted(offenders)[:20]})
    summary["order_holds"] = not any(item["cases"] for item in summary["order_violations"])
    summary["interpretation"] = (
        "Style and usefulness bars come from the rubric's own scale; coupling bars "
        "come from the upstream comment at the same location. Placement, the third "
        "part of effective, needs the placement corpus and is reported separately.")
    return summary


def score_rows(rows, corpus, file_judgments=None):
    """Criteria for every analyzable pair, per arm, plus the ladder summary."""
    by_id = {case["id"]: case for case in corpus}
    scored = {arm: [] for arm in ARMS}
    for row in rows:
        case = by_id.get(row["id"])
        if case is None:
            raise ValueError(f"Run row has no corpus case: {row['id']}")
        for arm in ARMS:
            judgment = (file_judgments or {}).get((case["path"], arm))
            scored[arm].append({"id": row["id"], "path": case["path"],
                                **case_criteria(row, case, arm, judgment)})
    return {"per_case": scored, "ladder": {arm: ladder(scored[arm]) for arm in ARMS}}


def measure_generations(output, corpus_loader):
    """Length and coupling for a run's saved comments, with no judgments needed.

    A run that was stopped before judging has already paid for its comments.
    Everything measurable without a judge is measured here, which is where the
    length question is settled: how closely a comment's length follows the
    length the location actually got upstream.
    """
    from statistics import correlation, linear_regression, mean, stdev

    output = Path(output).resolve()
    manifest = read_json(output / "manifest.json")
    corpus = corpus_loader(manifest)
    rows = []
    for case in corpus:
        comments = {}
        for arm in ARMS:
            answer = output / "calls" / f"{case['id']}-0" / arm / "answer.json"
            metadata = output / "calls" / f"{case['id']}-0" / arm / "metadata.json"
            if not answer.exists() or read_json(metadata).get("status") != "completed":
                break
            comments[arm] = read_json(answer)["comment"]
        if len(comments) != len(ARMS):
            continue
        comments["upstream"] = case["reference"]
        rows.append({"id": case["id"], "path": case["path"],
                     "length_band": case.get("length_band"),
                     "measures": {arm: measure_comment(text, case)
                                  for arm, text in comments.items()}})
    if not rows:
        raise ValueError("No complete pairs of saved generations in this run")
    reference = [row["measures"]["upstream"]["word_count"] for row in rows]
    summary = {"pairs": len(rows),
               "upstream_word_count_sd": stdev(reference) if len(reference) > 1 else 0.0}
    for arm in (*ARMS, "upstream"):
        lengths = [row["measures"][arm]["word_count"] for row in rows]
        summary[arm] = {
            "mean_word_count": mean(lengths),
            "word_count_sd": stdev(lengths) if len(lengths) > 1 else 0.0,
            "length_band_matches_upstream": sum(
                row["measures"][arm]["length_band"] == row["measures"]["upstream"]["length_band"]
                for row in rows) / len(rows),
            "mean_restatement_fraction": mean(
                row["measures"][arm]["restatement_fraction"] for row in rows),
            "mean_foreign_symbols_per_100_words": mean(
                row["measures"][arm]["foreign_symbols_per_100_words"] for row in rows),
        }
        if arm != "upstream" and len(rows) > 1:
            # A comment whose length followed the location would have slope near 1.
            summary[arm]["length_correlation_with_upstream"] = correlation(reference, lengths)
            summary[arm]["length_slope_against_upstream"] = linear_regression(reference, lengths).slope
    summary["bands"] = {}
    for band in sorted({row["length_band"] for row in rows if row["length_band"]}):
        subset = [row for row in rows if row["length_band"] == band]
        summary["bands"][band] = {"cases": len(subset), **{
            arm: mean(row["measures"][arm]["word_count"] for row in subset)
            for arm in (*ARMS, "upstream")}}
    summary["interpretation"] = (
        "Slope is how many words a comment gains for each word the upstream comment "
        "at that location has. One would mean length follows the location; zero means "
        "the same length everywhere regardless of what the code needs.")
    result = {"run": manifest["name"], "task_sha256": manifest["task_sha256"],
              "spec_sha256": manifest["spec_sha256"], "summary": summary, "per_case": rows}
    write_json(output / "generation-measures.json", result)
    return summary


def combine(runs):
    """Pool scored runs into one ladder per arm, keeping every case separate."""
    pooled = {arm: [] for arm in ARMS}
    for label, path in runs:
        result = read_json(Path(path).resolve() / "tiers.json")
        for arm in ARMS:
            for item in result["per_case"][arm]:
                pooled[arm].append({**item, "run": label})
    return {"runs": [label for label, _ in runs],
            "ladder": {arm: ladder(pooled[arm]) for arm in ARMS},
            "cases": {arm: len(pooled[arm]) for arm in ARMS}}


def score_run(output, corpus_loader):
    """Score a finished run and write tiers.json beside its other results."""
    output = Path(output).resolve()
    manifest = read_json(output / "manifest.json")
    rows = read_json(output / "results.json")
    corpus = corpus_loader(manifest)
    from .filelevel import JUDGMENTS
    judgment_path = output / JUDGMENTS
    file_judgments = None
    if judgment_path.exists():
        saved = read_json(judgment_path)
        if (saved.get("version") != 2 or saved["inputs"]["rows_sha256"] != digest(rows)
                or saved["inputs"]["corpus_sha256"] != digest(corpus)):
            raise ValueError("File judgments do not match this run's rows and corpus")
        file_judgments = {(item["path"], item["arm"]): item["optimal"]
                          for item in saved["files"]}
    result = score_rows(rows, corpus, file_judgments)
    result["run"] = manifest["name"]
    result["task_sha256"] = manifest["task_sha256"]
    result["spec_sha256"] = manifest["spec_sha256"]
    write_json(output / "tiers.json", result)
    return {"run": manifest["name"], "cases": len(rows),
            "ladder": {arm: result["ladder"][arm]["reached"] for arm in ARMS}}
